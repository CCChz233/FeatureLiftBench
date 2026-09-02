#!/usr/bin/env python3
"""Label paper-suite tasks against published FeatureLiftBench standards (v2).

Three labels, aggregated in this order:

1. any confirmed ``fail`` → ``violates``
2. else any ``undetermined`` → ``undetermined``
3. else → ``meets_standard``

Mechanical C1 hits and dangling entrypoints are ``undetermined`` until
adjudication.  Missing audits, missing ``valid`` fields, and uncovered oracle
rows are ``undetermined``, not violations.

Default output is a candidate directory under ``reports/``.  Official selection
files are written only with ``--write-selection``, and that flag is refused
while any task remains ``undetermined``.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TASKS = ROOT / "benchmark" / "python200_hard_tasks"
DEFAULT_CONSTITUTION = (
    ROOT / "reports" / "contract_closure_hard200_refresh" / "machine_audit.json"
)
DEFAULT_ENTRYPOINTS = (
    ROOT / "reports" / "paper_analysis" / "source_entrypoints_audit"
    / "source_entrypoints_audit.json"
)
DEFAULT_ORACLE = (
    ROOT / "reports" / "audits"
    / "python200_prime_oracle_revalidation" / "summary.json"
)
DEFAULT_OUTPUT = ROOT / "reports" / "paper_analysis" / "benchmark_tiers_v2_candidate"
DEFAULT_ADJUDICATIONS = DEFAULT_OUTPUT / "adjudications.csv"
V1_OUTPUT = ROOT / "reports" / "paper_analysis" / "benchmark_tiers"
OUTCOMES = (
    ROOT / "reports" / "paper_analysis" / "task_portability" / "task_portability.json"
)
PARENT_SUITE = ROOT / "benchmark" / "selection" / "python200_hard_suite.json"
SELECTION = ROOT / "benchmark" / "selection" / "python200_hard_standard_suite.json"
EXCLUDED = ROOT / "benchmark" / "selection" / "python200_hard_excluded.json"
STANDARD_TASK_FILE = (
    ROOT / "harness" / "config" / "experiments" / "python200_hard_standard.txt"
)
EXCLUDED_TASK_FILE = (
    ROOT / "harness" / "config" / "experiments" / "python200_hard_excluded.txt"
)
HARD50 = ROOT / "benchmark" / "hard50"
PROTOCOL_DOC = ROOT / "docs" / "BENCHMARK_VALIDATION_GATE.md"

sys.path.insert(0, str(ROOT / "harness" / "scripts"))

PROTOCOL_VERSION = "v2"
GATE_VERSION = "c1-scoped-v2"

RULES = {
    "R-PACKAGE": (
        "TASK_DESIGN_RULES.md §1–§4 / validate_constitution",
        "任务包未通过出题宪法校验",
    ),
    "R-ORACLE": (
        "python200_prime_oracle_revalidation",
        "参考解未通过或未覆盖三轮 Docker 复验",
    ),
    "R-SURFACE": (
        "TASK_DESIGN_RULES.md §2.1.1, §4.2.4 / GATE C1",
        "hidden 使用了 required_api 未声明的接口面",
    ),
    "R-ENTRY": (
        "BENCHMARK_VALIDATION_GATE.md C2",
        "source_entrypoints 在 pinned repo/ 中无法解析",
    ),
}

MEETS = "meets_standard"
VIOLATES = "violates"
UNDETERMINED = "undetermined"

ADJUDICATION_VERDICTS = {
    "confirmed_violation",
    "false_positive",
    "insufficient_evidence",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def sha256_tree(path: Path) -> str:
    digest = hashlib.sha256()
    if not path.exists():
        return sha256_bytes(b"")
    files = sorted(p for p in path.rglob("*") if p.is_file())
    for file in files:
        digest.update(file.relative_to(path).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(file.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def check(
    rule: str,
    *,
    status: str,
    mechanical_result: str,
    adjudication: str,
    evidence: list[Any],
    input_sha256: str,
) -> dict[str, Any]:
    return {
        "rule": rule,
        "status": status,
        "mechanical_result": mechanical_result,
        "adjudication": adjudication,
        "evidence": evidence,
        "input_sha256": input_sha256,
    }


def aggregate_label(checks: list[dict[str, Any]]) -> str:
    if any(item["status"] == "fail" for item in checks):
        return VIOLATES
    if any(item["status"] == "undetermined" for item in checks):
        return UNDETERMINED
    return MEETS


def apply_adjudication(
    mechanical: str,
    verdict: str | None,
) -> tuple[str, str]:
    """Return ``(status, adjudication)`` after optional human verdict."""
    if verdict == "confirmed_violation":
        return "fail", "confirmed_violation"
    if verdict == "false_positive":
        return "pass", "false_positive"
    if verdict == "insufficient_evidence":
        return "undetermined", "insufficient_evidence"
    if mechanical == "hit":
        return "undetermined", "pending"
    if mechanical == "error":
        return "undetermined", "pending"
    return "pass", "not_needed"


def load_refresh(path: Path) -> tuple[dict[str, dict[str, Any]], str]:
    if path.is_dir():
        path = path / "machine_audit.json"
    if not path.is_file():
        raise SystemExit(
            f"missing {path}; run scripts/audit_python200_contract_closure.py "
            "against the same suite first"
        )
    payload = json.loads(path.read_text(encoding="utf-8"))
    return (
        {task["task_id"]: task for task in payload.get("tasks", [])},
        sha256_file(path),
    )


def load_entrypoints(path: Path) -> tuple[dict[str, dict[str, Any]], str]:
    if not path.is_file():
        raise SystemExit(f"missing {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {row["task_id"]: row for row in payload.get("rows", [])}, sha256_file(path)


def load_oracle(path: Path) -> tuple[set[str], set[str], str]:
    if not path.is_file():
        raise SystemExit(f"missing {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    covered = {run["task_id"] for run in payload.get("runs", []) if run.get("task_id")}
    failed = set(payload.get("failed_task_ids") or [])
    failed |= set(payload.get("unstable_task_ids") or [])
    return covered, failed, sha256_file(path)


def load_adjudications(path: Path | None) -> dict[tuple[str, str], str]:
    if path is None or not path.is_file():
        return {}
    out: dict[tuple[str, str], str] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            task_id = (row.get("task_id") or "").strip()
            rule = (row.get("rule") or "").strip()
            verdict = (row.get("verdict") or "").strip()
            if not task_id or not rule:
                continue
            if verdict not in ADJUDICATION_VERDICTS:
                raise SystemExit(
                    f"invalid adjudication verdict {verdict!r} for {task_id} {rule}"
                )
            out[(task_id, rule)] = verdict
    return out


def load_outcomes() -> dict[str, dict[str, Any]]:
    if not OUTCOMES.is_file():
        return {}
    payload = json.loads(OUTCOMES.read_text(encoding="utf-8"))
    return {row["task_id"]: row for row in payload.get("rows", [])}


def _explicit_bool(block: Any, key: str) -> bool | None:
    if not isinstance(block, dict) or key not in block:
        return None
    value = block[key]
    return value if isinstance(value, bool) else None


def undeclared_surface(task: Path) -> tuple[str, list[str]]:
    """C1: members hidden tests exercise that ``required_api`` does not declare.

    Returns ``(mechanical_result, members)``.  ``hit`` does not by itself mean
    the task violates the standard; that requires adjudication.
    """
    from audit_contract_entailment import Contract, exercised_members

    hidden = task / "hidden_tests"
    if not hidden.is_dir():
        return "error", ["missing hidden_tests/"]
    try:
        metadata = json.loads((task / "metadata.json").read_text(encoding="utf-8"))
        public_spec = metadata.get("public_spec") or {}
        contract = Contract(public_spec)
        used = exercised_members(hidden, contract)
    except Exception as exc:  # noqa: BLE001 — mechanical checker failure
        return "error", [f"{type(exc).__name__}: {exc}"]
    members = sorted(
        member
        for member in used
        if member.split(".")[0] in contract.tops and member not in contract.members
    )
    return ("hit" if members else "clear"), members


def label(
    tasks_root: Path,
    constitution_audit: Path,
    entrypoints_audit: Path,
    oracle_summary: Path,
    adjudications: dict[tuple[str, str], str],
    adjudications_path: Path | None = None,
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    refresh, constitution_hash = load_refresh(constitution_audit)
    entrypoints, entrypoints_hash = load_entrypoints(entrypoints_audit)
    covered, unstable, oracle_hash = load_oracle(oracle_summary)
    protocol_hash = sha256_file(PROTOCOL_DOC) if PROTOCOL_DOC.is_file() else ""
    parent_hash = sha256_file(PARENT_SUITE) if PARENT_SUITE.is_file() else ""
    parent_task_set = ""
    if PARENT_SUITE.is_file():
        parent_task_set = str(
            json.loads(PARENT_SUITE.read_text(encoding="utf-8")).get("task_set_sha256")
            or ""
        )
    if adjudications_path is not None and adjudications_path.is_file():
        adjudications_hash = sha256_file(adjudications_path)
    else:
        adjudications_hash = sha256_bytes(b"")
    inputs = {
        "protocol_version": PROTOCOL_VERSION,
        "gate_version": GATE_VERSION,
        "protocol_sha256": protocol_hash,
        "parent_suite_sha256": parent_hash,
        "parent_task_set_sha256": parent_task_set,
        "constitution_audit_sha256": constitution_hash,
        "entrypoints_audit_sha256": entrypoints_hash,
        "oracle_summary_sha256": oracle_hash,
        "adjudications_sha256": adjudications_hash,
    }

    rows: list[dict[str, Any]] = []
    for task_dir in sorted(tasks_root.iterdir()):
        if not task_dir.is_dir() or not (task_dir / "metadata.json").is_file():
            continue
        task_id = task_dir.name
        metadata = json.loads((task_dir / "metadata.json").read_text(encoding="utf-8"))
        spec_hash = str(metadata.get("spec_hash") or "")
        task_revision = metadata.get("task_revision")
        record = refresh.get(task_id, {})
        task_input = sha256_bytes(
            json.dumps(
                {
                    "spec_hash": spec_hash,
                    "task_revision": task_revision,
                    "hidden": sha256_tree(task_dir / "hidden_tests"),
                    "entrypoints": metadata.get("public_spec", {}).get(
                        "source_entrypoints"
                    ),
                },
                sort_keys=True,
            ).encode("utf-8")
        )
        checks: list[dict[str, Any]] = []

        if task_id not in refresh:
            checks.append(
                check(
                    "R-PACKAGE",
                    status="undetermined",
                    mechanical_result="error",
                    adjudication="pending",
                    evidence=["未纳入 constitution 审计"],
                    input_sha256=constitution_hash,
                )
            )
        else:
            strict = _explicit_bool(record.get("strict_validation"), "valid")
            runnable = _explicit_bool(record.get("runnable_validation"), "valid")
            if strict is None or runnable is None:
                checks.append(
                    check(
                        "R-PACKAGE",
                        status="undetermined",
                        mechanical_result="error",
                        adjudication="pending",
                        evidence=["strict/runnable valid 字段缺失"],
                        input_sha256=constitution_hash,
                    )
                )
            elif strict and runnable:
                checks.append(
                    check(
                        "R-PACKAGE",
                        status="pass",
                        mechanical_result="clear",
                        adjudication="not_needed",
                        evidence=[],
                        input_sha256=constitution_hash,
                    )
                )
            else:
                errors = (record.get("strict_validation") or {}).get("errors") or []
                checks.append(
                    check(
                        "R-PACKAGE",
                        status="fail",
                        mechanical_result="hit",
                        adjudication="not_needed",
                        evidence=errors[:4],
                        input_sha256=constitution_hash,
                    )
                )

        if task_id not in covered:
            checks.append(
                check(
                    "R-ORACLE",
                    status="undetermined",
                    mechanical_result="error",
                    adjudication="pending",
                    evidence=["未纳入复验"],
                    input_sha256=oracle_hash,
                )
            )
        elif task_id in unstable:
            checks.append(
                check(
                    "R-ORACLE",
                    status="fail",
                    mechanical_result="hit",
                    adjudication="not_needed",
                    evidence=["复验失败或不稳定"],
                    input_sha256=oracle_hash,
                )
            )
        else:
            checks.append(
                check(
                    "R-ORACLE",
                    status="pass",
                    mechanical_result="clear",
                    adjudication="not_needed",
                    evidence=[],
                    input_sha256=oracle_hash,
                )
            )

        mechanical, members = undeclared_surface(task_dir)
        status, adjudication = apply_adjudication(
            mechanical, adjudications.get((task_id, "R-SURFACE"))
        )
        checks.append(
            check(
                "R-SURFACE",
                status=status,
                mechanical_result=mechanical,
                adjudication=adjudication,
                evidence=members,
                input_sha256=task_input,
            )
        )

        entry = entrypoints.get(task_id)
        if entry is None:
            entry_mechanical, entry_evidence = "error", ["未纳入入口审计"]
        else:
            worst = entry.get("worst")
            dangling = [
                item.get("symbol")
                for item in entry.get("entries") or []
                if item.get("verdict") == "dangling"
            ]
            if worst == "dangling":
                entry_mechanical, entry_evidence = "hit", dangling or ["dangling"]
            elif worst == "undecidable":
                entry_mechanical, entry_evidence = "error", ["入口审计 undecidable"]
            elif worst in {"resolved", "misplaced", "undeclared"}:
                entry_mechanical, entry_evidence = "clear", []
            else:
                entry_mechanical, entry_evidence = "error", [f"未知入口判定 {worst!r}"]
        status, adjudication = apply_adjudication(
            entry_mechanical, adjudications.get((task_id, "R-ENTRY"))
        )
        checks.append(
            check(
                "R-ENTRY",
                status=status,
                mechanical_result=entry_mechanical,
                adjudication=adjudication,
                evidence=entry_evidence,
                input_sha256=entrypoints_hash,
            )
        )

        rows.append(
            {
                "task_id": task_id,
                "label": aggregate_label(checks),
                "lift_type": record.get("lift_type"),
                "spec_hash": spec_hash,
                "task_revision": task_revision,
                "checks": checks,
            }
        )
    return rows, inputs


def _doc_link(output: Path, relative: str) -> str:
    target = ROOT / relative
    return Path(os.path.relpath(target, output)).as_posix()


def render(rows: list[dict[str, Any]], output: Path, inputs: dict[str, str]) -> str:
    outcomes = load_outcomes()
    rules_doc = _doc_link(output, "docs/TASK_DESIGN_RULES.md")
    labels = Counter(row["label"] for row in rows)
    pending = [
        (row["task_id"], item)
        for row in rows
        for item in row["checks"]
        if item["adjudication"] == "pending"
    ]
    out = ["# Python-200 题目标准符合性标签（v2 候选）", ""]
    out.append(f"> **Protocol: {PROTOCOL_VERSION} · Gate: {GATE_VERSION} · 非正式名单**")
    out.append("")
    out.append(
        f"对照 [TASK_DESIGN_RULES.md]({rules_doc})。"
        "C1 命中与入口悬空在裁决前标 `undetermined`，不直接标 `violates`。"
        "`__getitem__` 等协议方法必须写进 `required_api`，不得按“缓存天然支持下标”豁免。"
    )
    out.append("")
    out.append("## 结论")
    out.append("")
    out.append(
        f"论文套件 {len(rows)} 道：**{labels.get(MEETS, 0)} 符合**，"
        f"**{labels.get(VIOLATES, 0)} 已确认违反**，"
        f"**{labels.get(UNDETERMINED, 0)} 待定**。"
        "待定非空时不得发布分析名单。"
    )
    out.append("")
    out.append("## 输入哈希")
    out.append("")
    for key, value in inputs.items():
        out.append(f"- `{key}`: `{value}`")
    out.append("")

    if pending:
        out.append(f"## 裁决队列（{len(pending)} 条）")
        out.append("")
        out.append("| 题 | 条款 | 机械结果 | 证据 |")
        out.append("| :-- | :-- | :-- | :-- |")
        for task_id, item in pending:
            evidence = ", ".join(str(x) for x in item["evidence"][:4])
            out.append(
                f"| `{task_id}` | `{item['rule']}` | {item['mechanical_result']} | {evidence} |"
            )
        out.append("")

    failed = [row for row in rows if row["label"] == VIOLATES]
    if failed:
        out.append(f"## 已确认违反（{len(failed)}）")
        out.append("")
        out.append("| 题 | 条款 |")
        out.append("| :-- | :-- |")
        for row in failed:
            rules = ", ".join(
                f"`{item['rule']}`"
                for item in row["checks"]
                if item["status"] == "fail"
            )
            out.append(f"| `{row['task_id']}` | {rules} |")
        out.append("")

    if outcomes:
        out.append("## 与主实验交叉")
        out.append("")
        out.append("| 标签 | 有结果的题 | 通过率 |")
        out.append("| :-- | ---: | ---: |")
        for label in (MEETS, VIOLATES, UNDETERMINED):
            subset = [
                outcomes[row["task_id"]]
                for row in rows
                if row["label"] == label and row["task_id"] in outcomes
            ]
            if not subset:
                out.append(f"| `{label}` | 0 | - |")
                continue
            passed = sum(1 for item in subset if item["pass"])
            out.append(
                f"| `{label}` | {len(subset)} | {passed}/{len(subset)} "
                f"({passed / len(subset):.0%}) |"
            )
        out.append("")
    return "\n".join(out) + "\n"


def write_queue(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "task_id",
        "rule",
        "mechanical_result",
        "status",
        "adjudication",
        "evidence",
        "spec_hash",
        "task_revision",
    ]
    pending = [
        {
            "task_id": row["task_id"],
            "rule": item["rule"],
            "mechanical_result": item["mechanical_result"],
            "status": item["status"],
            "adjudication": item["adjudication"],
            "evidence": ";".join(str(x) for x in item["evidence"]),
            "spec_hash": row["spec_hash"],
            "task_revision": row["task_revision"],
        }
        for row in rows
        for item in row["checks"]
        if item["adjudication"] == "pending"
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(pending)


def _task_set_sha256(task_ids: list[str]) -> str:
    return sha256_bytes(("\n".join(task_ids) + "\n").encode("utf-8"))


def write_selection(rows: list[dict[str, Any]], inputs: dict[str, str]) -> None:
    undetermined = [row["task_id"] for row in rows if row["label"] == UNDETERMINED]
    if undetermined:
        raise SystemExit(
            f"refusing --write-selection: {len(undetermined)} undetermined tasks remain"
        )
    parent = json.loads(PARENT_SUITE.read_text(encoding="utf-8"))
    parent_ids = [str(item) for item in parent["task_ids"]]
    labeled = {row["task_id"] for row in rows}
    if labeled != set(parent_ids):
        raise SystemExit("labels must cover the parent suite exactly")

    keep = sorted(row["task_id"] for row in rows if row["label"] == MEETS)
    drop = [row for row in rows if row["label"] == VIOLATES]
    hard50 = (
        {path.name for path in HARD50.iterdir() if path.is_dir()}
        if HARD50.is_dir()
        else set()
    )
    payload = {
        "schema_version": "featureliftbench.python200_hard_standard_suite.v2",
        "suite_id": "python200-hard-standard-unreleased",
        "parent_suite_id": parent["suite_id"],
        "label_protocol": "docs/BENCHMARK_VALIDATION_GATE.md",
        "protocol_version": PROTOCOL_VERSION,
        "gate_version": GATE_VERSION,
        **inputs,
        "task_root": parent["task_root"],
        "source_registry": parent["source_registry"],
        "task_count": len(keep),
        "parent_task_count": len(parent_ids),
        "excluded_count": len(drop),
        "baseline_count": sum(1 for task_id in keep if task_id not in hard50),
        "hard50_count": sum(1 for task_id in keep if task_id in hard50),
        "task_set_sha256": _task_set_sha256(keep),
        "task_ids": keep,
    }
    SELECTION.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    EXCLUDED.write_text(
        json.dumps(
            {
                "schema_version": "featureliftbench.python200_hard_excluded.v2",
                "parent_suite_id": parent["suite_id"],
                "protocol_version": PROTOCOL_VERSION,
                "n": len(drop),
                "tasks": [
                    {
                        "task_id": row["task_id"],
                        "failed_rules": [
                            item["rule"]
                            for item in row["checks"]
                            if item["status"] == "fail"
                        ],
                        "checks": row["checks"],
                    }
                    for row in drop
                ],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    STANDARD_TASK_FILE.write_text("\n".join(keep) + "\n", encoding="utf-8")
    EXCLUDED_TASK_FILE.write_text(
        "\n".join(row["task_id"] for row in drop) + "\n", encoding="utf-8"
    )
    print(f"wrote {SELECTION.relative_to(ROOT)} ({len(keep)} tasks)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks-root", type=Path, default=DEFAULT_TASKS)
    parser.add_argument("--constitution-audit", type=Path, default=DEFAULT_CONSTITUTION)
    parser.add_argument("--entrypoints-audit", type=Path, default=DEFAULT_ENTRYPOINTS)
    parser.add_argument("--oracle-summary", type=Path, default=DEFAULT_ORACLE)
    parser.add_argument("--adjudications", type=Path, default=DEFAULT_ADJUDICATIONS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--write-selection",
        action="store_true",
        help="write official analysis suite files; refused while undetermined remains",
    )
    args = parser.parse_args()
    print(
        "warning: screening is paused; daily gate is scripts/run_benchmark_gate.py. "
        "--write-selection is refused while any task is undetermined.",
        file=sys.stderr,
    )

    adjudications = load_adjudications(args.adjudications)
    if args.output.resolve() == V1_OUTPUT.resolve():
        raise SystemExit(
            "refusing to overwrite v1 reports at "
            f"{V1_OUTPUT.relative_to(ROOT)}; use {DEFAULT_OUTPUT.relative_to(ROOT)}"
        )
    rows, inputs = label(
        args.tasks_root,
        args.constitution_audit,
        args.entrypoints_audit,
        args.oracle_summary,
        adjudications,
        args.adjudications,
    )
    labeled_ids = [row["task_id"] for row in rows]
    if len(labeled_ids) != len(set(labeled_ids)):
        raise SystemExit("duplicate task ids in labeler output")
    if args.tasks_root.resolve() == DEFAULT_TASKS.resolve() and PARENT_SUITE.is_file():
        parent_ids = {
            str(item)
            for item in json.loads(PARENT_SUITE.read_text(encoding="utf-8"))["task_ids"]
        }
        if set(labeled_ids) != parent_ids:
            raise SystemExit(
                "labeled task ids must equal the parent Python-200′ suite"
            )
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "labels.json").write_text(
        json.dumps(
            {
                "n": len(rows),
                "protocol_version": PROTOCOL_VERSION,
                "gate_version": GATE_VERSION,
                "tasks_root": str(args.tasks_root),
                "inputs": inputs,
                "rules": {key: source for key, (source, _) in RULES.items()},
                "rows": rows,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    (args.output / "labels.md").write_text(
        render(rows, args.output, inputs), encoding="utf-8"
    )

    by_label: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        by_label[row["label"]].append(row["task_id"])
    (args.output / "meets_standard_candidate.txt").write_text(
        "\n".join(by_label.get(MEETS, [])) + ("\n" if by_label.get(MEETS) else ""),
        encoding="utf-8",
    )
    (args.output / "violates_confirmed.txt").write_text(
        "\n".join(by_label.get(VIOLATES, [])) + ("\n" if by_label.get(VIOLATES) else ""),
        encoding="utf-8",
    )
    (args.output / "undetermined.txt").write_text(
        "\n".join(by_label.get(UNDETERMINED, []))
        + ("\n" if by_label.get(UNDETERMINED) else ""),
        encoding="utf-8",
    )
    write_queue(args.output / "adjudication_queue.csv", rows)

    print({name: len(ids) for name, ids in sorted(by_label.items())})
    print(f"wrote {args.output}")

    if args.write_selection:
        write_selection(rows, inputs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
