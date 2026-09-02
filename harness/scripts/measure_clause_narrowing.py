#!/usr/bin/env python3
"""Measure whether Hidden-only failures were caused by missing or narrowed obligations.

A Hidden-first failure means the agent passed everything it could see and failed
only on tests it could not. Two very different mechanisms produce that outcome:

- the public contract never determined the obligation, so no amount of agent
  effort could recover it; or
- the contract did state the obligation and the agent implemented a strictly
  weaker reading that its own tests still satisfy.

The distinction decides where improvement has to happen, so this script builds
one evidence packet per failure -- failing assertion, the clause it is mapped to,
and the submission code behind it -- and then summarizes a hand-labeled verdict.

Only Hidden-first failures are in scope. A Public failure means the agent had the
test in hand and did not run or fix it, which says nothing about how it reads
contract text.
"""

from __future__ import annotations

import argparse
import ast
import csv
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_contract_entailment import Contract, _UsageVisitor  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BENCHMARK = ROOT / "benchmark" / "python200_hard_tasks"

FAILED_RE = re.compile(r"^(?:FAILED|ERROR)\s+(\S+)", re.MULTILINE)
ASSERT_RE = re.compile(r"^E\s+(.*)$", re.MULTILINE)

# Was the obligation the hidden test checks recoverable from the public contract?
OBLIGATION_STATUS = {
    "stated": "契约已判定：条款或 required_api 足以确定该断言",
    "scope_open": "范围开放：义务已写明，但适用入口/目标未指定",
    "value_open": "取值开放：期望值或异常类型无法从契约推出",
    "contradicted": "契约相反：声明的签名或条款与隐藏断言不相容",
    "absent": "契约未涉及该义务",
    "undecided": "证据不足",
}

# Obligations an agent could in principle have recovered from the contract alone.
RECOVERABLE = {"stated", "scope_open"}

# What the submission did, meaningful only when the obligation was recoverable.
AGENT_BEHAVIOR = {
    "narrowed": "窄化：实现满足义务的一个投影，不满足义务本身",
    "contrary": "相反：实现了另一套自洽语义（通常照搬上游）",
    "absent": "缺失：完全未实现该义务",
    "attempted_buggy": "已实现但运行时不成立：普通实现缺陷，与契约解释无关",
    "na": "不适用",
    "undecided": "证据不足",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def hidden_first_failures(run_dir: Path) -> list[str]:
    """Tasks that built, passed every visible test, and failed only on Hidden."""
    found: list[str] = []
    for task in sorted(run_dir.iterdir()):
        result = task / "eval" / "result.json"
        if not result.is_file():
            continue
        data = read_json(result)
        if (
            data.get("build_pass")
            and data.get("public_tests_pass")
            and not data.get("hidden_tests_pass")
        ):
            found.append(task.name)
    return found


def failing_tests(run_dir: Path, task_id: str) -> tuple[list[str], list[str]]:
    log = run_dir / task_id / "eval" / "logs" / "hidden.stdout"
    if not log.is_file():
        return [], []
    text = log.read_text(encoding="utf-8", errors="replace")
    nodeids = [n.split("::", 1)[-1] for n in FAILED_RE.findall(text)]
    assertions = [a.strip() for a in ASSERT_RE.findall(text) if a.strip()]
    return nodeids, assertions[:8]


def locate_test(hidden_dir: Path, test_name: str) -> tuple[Path | None, str]:
    for path in sorted(hidden_dir.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == test_name:
                return path, ast.get_source_segment(text, node) or ""
    return None, ""


def file_symbols(path: Path, contract: Contract) -> set[str]:
    """Members the whole test module drives.

    The visitor tracks names bound by ``import featurelifted``, so it has to see
    the module rather than one function body.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return set()
    visitor = _UsageVisitor(contract)
    visitor.visit(tree)
    return visitor.used


def mapped_clauses(metadata: dict[str, Any], test_name: str) -> tuple[list[str], list[str]]:
    """Clause ids declared for this test, plus their contract text."""
    spec = metadata.get("evaluation_spec") or {}
    public = metadata.get("public_spec") or {}
    texts = {b.get("id"): b.get("text", "") for b in public.get("behaviors") or []}
    ids: list[str] = []
    for mapping in spec.get("hidden_test_mappings") or []:
        if mapping.get("nodeid", "").endswith(f"::{test_name}"):
            ids.extend(mapping.get("behavior_ids") or [])
    ids = sorted(set(ids))
    return ids, [f"{cid}: {texts.get(cid, '(clause text not found)')}" for cid in ids]


def submission_definitions(submission: Path, symbols: set[str]) -> dict[str, str]:
    """Source of the submission symbols the failing test drives."""
    wanted = {s.split(".")[0] for s in symbols} | {s.split(".")[-1] for s in symbols}
    found: dict[str, str] = {}
    for path in sorted(submission.rglob("*.py")):
        try:
            text = path.read_text(encoding="utf-8")
            tree = ast.parse(text)
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            if node.name in wanted and node.name not in found:
                segment = ast.get_source_segment(text, node) or ""
                found[node.name] = segment[:2000]
    return found


def build_packet(run_dir: Path, benchmark: Path, task_id: str) -> dict[str, Any]:
    task = benchmark / task_id
    metadata = read_json(task / "metadata.json")
    contract = Contract(metadata.get("public_spec") or {})
    names, assertions = failing_tests(run_dir, task_id)

    tests: list[dict[str, Any]] = []
    symbols: set[str] = set()
    for name in names:
        path, source = locate_test(task / "hidden_tests", name)
        if path is not None:
            symbols |= file_symbols(path, contract)
        ids, texts = mapped_clauses(metadata, name)
        tests.append(
            {"test": name, "source": source, "clause_ids": ids, "clause_texts": texts}
        )

    submission = run_dir / task_id / "submission"
    return {
        "task_id": task_id,
        "failing_tests": tests,
        "assertion_evidence": assertions,
        "symbols_exercised": sorted(symbols),
        "declared_members": sorted(contract.members),
        "submission_definitions": submission_definitions(submission, symbols)
        if submission.is_dir()
        else {},
    }


def render_packets(packets: list[dict[str, Any]]) -> str:
    out = ["# Hidden 首败逐题证据包", ""]
    out.append(
        "> 每题给出：失败断言、该测试声明映射到的契约条款原文、"
        "以及提交中对应符号的实现。用于判定义务是否已被契约确定。"
    )
    out.append("")
    for packet in packets:
        out.append(f"## `{packet['task_id']}`")
        out.append("")
        for test in packet["failing_tests"]:
            out.append(f"### 失败用例 `{test['test']}`")
            out.append("")
            out.append(f"声明映射条款：{', '.join(test['clause_ids']) or '（无映射）'}")
            out.append("")
            for text in test["clause_texts"]:
                out.append(f"- {text}")
            out.append("")
            if test["source"]:
                out.append("```python")
                out.append(test["source"])
                out.append("```")
                out.append("")
        if packet["assertion_evidence"]:
            out.append("失败证据：")
            out.append("")
            out.append("```text")
            out.extend(packet["assertion_evidence"])
            out.append("```")
            out.append("")
        undeclared = [
            s for s in packet["symbols_exercised"] if s not in packet["declared_members"]
        ]
        if undeclared:
            out.append(f"测试驱动但未在 `required_api` 声明的成员：`{'; '.join(undeclared)}`")
            out.append("")
        for name, source in packet["submission_definitions"].items():
            out.append(f"提交实现 `{name}`：")
            out.append("")
            out.append("```python")
            out.append(source)
            out.append("```")
            out.append("")
    return "\n".join(out) + "\n"


def summarize(packets: list[dict[str, Any]], labels: dict[str, dict[str, str]]) -> str:
    total = len(packets)
    status = Counter(labels.get(p["task_id"], {}).get("obligation_status", "unlabeled") for p in packets)
    behavior = Counter(
        labels.get(p["task_id"], {}).get("agent_behavior", "unlabeled")
        for p in packets
        if labels.get(p["task_id"], {}).get("obligation_status") in RECOVERABLE
    )
    recoverable = sum(status.get(k, 0) for k in RECOVERABLE)

    out = ["# Hidden 首败：义务是否已被契约确定", ""]
    out.append(
        "> **Status: AI 初标，非 human gold · 单一模型单次运行**"
    )
    out.append("")
    out.append("## 口径")
    out.append("")
    out.append(
        f"分母为整场主实验中 **Hidden 首败**的 {total} 题，即 build 与全部可见测试通过、"
        "仅隐藏测试失败的运行。Public 首败不计入：那类失败中 Agent 手里就有测试，"
        "反映的是未运行或未修复，与契约文本的解释无关。"
    )
    out.append("")
    out.append("## 结果")
    out.append("")
    out.append("| 义务状态 | 题数 | 含义 |")
    out.append("| --- | ---: | --- |")
    for key, label in OBLIGATION_STATUS.items():
        if status.get(key):
            out.append(f"| `{key}` | {status[key]} | {label} |")
    out.append("")
    if recoverable:
        out.append(
            f"**{recoverable}/{total}** 题的义务可从公开契约恢复（`stated` + `scope_open`）。"
            "这部分失败不是信息缺失，补充信息不会改善，改进必须作用在 Agent 如何解释与验证义务上。"
        )
        out.append("")
        out.append(
            f"其余 **{total - recoverable}/{total}** 题无法由契约恢复，属于基准侧缺陷："
            "任何作用于 Agent 的方法改进都无法覆盖，只能改题。这构成本次运行中"
            "方法类改进的可达上限。"
        )
        out.append("")
        out.append("| 可恢复义务下的 Agent 行为 | 题数 | 含义 |")
        out.append("| --- | ---: | --- |")
        for key, label in AGENT_BEHAVIOR.items():
            if behavior.get(key):
                out.append(f"| `{key}` | {behavior[key]} | {label} |")
        out.append("")
    out.append("## 逐题")
    out.append("")
    out.append("| 任务 | 义务状态 | Agent 行为 | 依据 |")
    out.append("| --- | --- | --- | --- |")
    for packet in sorted(packets, key=lambda p: p["task_id"]):
        row = labels.get(packet["task_id"], {})
        reason = (row.get("reason") or "—").replace("|", "\\|")
        out.append(
            f"| `{packet['task_id']}` | `{row.get('obligation_status', 'unlabeled')}` "
            f"| `{row.get('agent_behavior', 'na')}` | {reason} |"
        )
    out.append("")
    out.append("## 限制")
    out.append("")
    out.append(
        f"- n={total}，单模型单次运行，比例不可外推到其他模型或其他 split。"
    )
    out.append(
        "- 标注为 AI 初标。论文使用前需第二位独立标注者按同一证据包复核，并报告一致性。"
    )
    out.append(
        "- `stated` 与 `scope_open` 的边界依赖对条款措辞的判断，是本测量最主要的分歧来源。"
    )
    return "\n".join(out) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True, help="suite run directory")
    parser.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK)
    parser.add_argument("--labels", type=Path, help="CSV of hand labels; omit to emit a template")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    task_ids = hidden_first_failures(args.run)
    packets = [build_packet(args.run, args.benchmark, tid) for tid in task_ids]

    labels: dict[str, dict[str, str]] = {}
    if args.labels and args.labels.exists():
        with args.labels.open(newline="", encoding="utf-8") as handle:
            for record in csv.DictReader(handle):
                if record["obligation_status"] not in OBLIGATION_STATUS:
                    raise ValueError(f"invalid obligation_status for {record['task_id']}")
                if record.get("agent_behavior") and record["agent_behavior"] not in AGENT_BEHAVIOR:
                    raise ValueError(f"invalid agent_behavior for {record['task_id']}")
                labels[record["task_id"]] = record

    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "evidence_packets.json").write_text(
        json.dumps(
            {"generated_at": datetime.now(timezone.utc).isoformat(),
             "run": str(args.run), "packets": packets},
            indent=2, ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )
    (args.output / "evidence_packets.md").write_text(render_packets(packets), encoding="utf-8")

    if not labels:
        write_csv(
            args.output / "labels_template.csv",
            [{"task_id": t, "obligation_status": "", "agent_behavior": "", "reason": ""}
             for t in task_ids],
        )
        print(f"emitted {len(packets)} evidence packets and a blank label template")
    else:
        (args.output / "clause_narrowing.md").write_text(
            summarize(packets, labels), encoding="utf-8"
        )
        print(f"summarized {len(packets)} hidden-first failures")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
