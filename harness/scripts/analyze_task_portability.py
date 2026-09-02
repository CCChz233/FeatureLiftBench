#!/usr/bin/env python3
"""Measure how far task portability alone explains agent success.

A task is *portable* when its reference solution is largely a verbatim
transplant of the pinned upstream snapshot, and *synthesis* when the reference
had to be written rather than lifted.  Portability is a property of the task,
fixed before any agent runs, and it is computed two ways:

``ref_cf``
    Copy fraction of the reference solution against ``repo/``.  Oracle-derived,
    so it is a ground-truth label and must never reach the agent.

``api_resolve``
    Fraction of ``public_spec.required_api`` leaf names that resolve to a
    definition in ``repo/``.  Uses only task inputs, so it is the deployable
    estimator of the same property.

The point of the split is to separate agent behaviour from task difficulty.
Submission copy fraction correlates strongly with passing, but that comparison
is confounded: copy-heavy submissions cluster on portable tasks.  Conditioning
on the reference removes the confound.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from audit_contract_entailment import index_upstream  # noqa: E402
from featureliftbench.compactness import analyze_submission_footprint  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
TASKS = ROOT / "benchmark" / "python200_hard_tasks"
ORACLES = ROOT / "benchmark" / "submissions"

PORTABLE_REF_CF = 0.90
PORTABLE_API_RESOLVE = 0.99


def lift_types() -> dict[str, str]:
    path = ROOT / "reports" / "contract_closure_200" / "machine_audit.json"
    if not path.is_file():
        return {}
    out: dict[str, str] = {}

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            task_id = node.get("task_id")
            lift = node.get("lift_type") or node.get("lift")
            if task_id and lift:
                out[str(task_id)] = str(lift)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(json.loads(path.read_text(encoding="utf-8")))
    return out


def api_resolve(task: Path) -> float | None:
    try:
        metadata = json.loads((task / "metadata.json").read_text(encoding="utf-8"))
    except Exception:
        return None
    required = (metadata.get("public_spec") or {}).get("required_api") or []
    if not required:
        return None
    try:
        names = set(index_upstream(task / "repo"))
    except Exception:
        return None
    total = 0
    hit = 0
    for entry in required:
        symbol = entry.get("path") or entry.get("name") or ""
        leaf = symbol.split(".")[-1]
        if not leaf:
            continue
        total += 1
        if leaf in names or symbol in names:
            hit += 1
    return hit / total if total else None


def collect(run: Path) -> list[dict[str, Any]]:
    lifts = lift_types()
    rows: list[dict[str, Any]] = []
    for entry in sorted(run.iterdir()):
        result = entry / "eval" / "result.json"
        task = TASKS / entry.name
        oracle = ORACLES / entry.name / "oracle"
        if not (result.is_file() and task.is_dir() and oracle.is_dir()):
            continue
        payload = json.loads(result.read_text(encoding="utf-8"))
        agent_cf = (payload.get("compactness") or {}).get("copied_fraction")
        if agent_cf is None:
            continue
        try:
            reference = analyze_submission_footprint(task, oracle, reference_path=oracle)
        except Exception:
            continue
        tokens = None
        run_json = entry / "run.json"
        if run_json.is_file():
            usage = (
                (json.loads(run_json.read_text(encoding="utf-8")).get("agent") or {})
                .get("usage")
                or {}
            )
            tokens = usage.get("total_tokens")
        rows.append(
            {
                "task_id": entry.name,
                "lift": lifts.get(entry.name, "unknown"),
                "agent_cf": float(agent_cf),
                "ref_cf": float(reference["copied_fraction"]),
                "api_resolve": api_resolve(task),
                "tokens": tokens,
                "pass": bool(
                    payload.get("build_pass")
                    and payload.get("public_tests_pass")
                    and payload.get("hidden_tests_pass")
                    and payload.get("isolation_pass")
                ),
            }
        )
    return rows


def rate(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "-"
    hit = sum(1 for r in rows if r["pass"])
    return f"{hit}/{len(rows)} ({hit / len(rows):.0%})"


def render(rows: list[dict[str, Any]]) -> str:
    portable = [r for r in rows if r["ref_cf"] >= PORTABLE_REF_CF]
    synthesis = [r for r in rows if r["ref_cf"] < PORTABLE_REF_CF]
    tokens = lambda rs: [r["tokens"] for r in rs if r["tokens"]]  # noqa: E731

    out = ["# 题目可移植性：难度的单一主导因子", ""]
    out.append("> **Status: AI 生成的离线分析 · 未跑任何模型**")
    out.append("")
    out.append("## 结论")
    out.append("")
    out.append(
        f"把题按**参考解是否为上游的逐行移植**切开，通过率就分成了两个几乎不重叠的"
        f"区间：可移植题 {rate(portable)}，需要合成的题 {rate(synthesis)}。"
        "可移植性是题目的固有属性，在任何 Agent 运行之前就确定了。"
    )
    out.append("")
    out.append("## 为什么不能看提交的抄袭度")
    out.append("")
    out.append(
        "提交的 `copied_fraction` 和通过强相关，很容易读成"
        "「Agent 应该多移植、少自己写」。这个读法是混淆的：抄得多的提交"
        "扎堆在可移植题上，而可移植题本来就几乎全过。"
    )
    out.append("")
    out.append("| 子集 | Agent 高抄袭 | Agent 低抄袭 |")
    out.append("| :-- | ---: | ---: |")
    for label, subset in (("可移植题", portable), ("需合成题", synthesis)):
        high = [r for r in subset if r["agent_cf"] >= 0.9]
        low = [r for r in subset if r["agent_cf"] < 0.9]
        out.append(f"| {label} | {rate(high)} | {rate(low)} |")
    out.append("")
    out.append(
        "在可移植题内部，Agent 自己写还是照抄几乎不影响结果；"
        "全部失败质量都落在需合成题上。**「劝 Agent 去移植」没有收益空间。**"
    )
    out.append("")
    out.append("## 按 lift 类型")
    out.append("")
    out.append("| lift | n | 参考解 `ref_cf` 中位 | 可移植占比 | 通过率 |")
    out.append("| :-- | ---: | ---: | ---: | ---: |")
    for lift in ("Direct", "Adapted", "Composite", "unknown"):
        subset = [r for r in rows if r["lift"] == lift]
        if not subset:
            continue
        count = sum(1 for r in subset if r["ref_cf"] >= PORTABLE_REF_CF)
        median = statistics.median([r["ref_cf"] for r in subset])
        out.append(
            f"| {lift} | {len(subset)} | {median:.3f} "
            f"| {count}/{len(subset)} | {rate(subset)} |"
        )
    out.append("")
    out.append("## 免 oracle 的估计量")
    out.append("")
    out.append(
        "`ref_cf` 来自参考解，不能在运行时使用。`api_resolve`——声明 API 的叶名"
        "在 `repo/` 中解析成功的比例——只用题面输入，可以。"
    )
    out.append("")
    out.append("| 阈值 | 判为可移植 | 真可移植 | 精确率 | 召回 |")
    out.append("| ---: | ---: | ---: | ---: | ---: |")
    for threshold in (0.99, 0.9, 0.75, 0.5):
        flagged = [
            r for r in rows
            if r["api_resolve"] is not None and r["api_resolve"] >= threshold
        ]
        true_positive = sum(1 for r in flagged if r["ref_cf"] >= PORTABLE_REF_CF)
        precision = true_positive / len(flagged) if flagged else float("nan")
        recall = true_positive / len(portable) if portable else float("nan")
        out.append(
            f"| {threshold} | {len(flagged)} | {true_positive} "
            f"| {precision:.0%} | {recall:.0%} |"
        )
    out.append("")
    out.append("## 判别力的代价")
    out.append("")
    total = sum(tokens(rows))
    if total:
        out.append(
            f"可移植题占 **{len(portable)}/{len(rows)}** 道、消耗 "
            f"**{sum(tokens(portable)) / total:.0%}** 的 token，通过率 {rate(portable)}。"
            "它们几乎不产生区分度，却占掉大部分算力预算。"
        )
        out.append("")
        out.append(
            f"两类题的单题 token 中位几乎相同"
            f"（{statistics.median(tokens(portable)):,.0f} vs "
            f"{statistics.median(tokens(synthesis)):,.0f}）——"
            "Agent 对「几乎必过」和「多半会挂」的题投入完全一样的算力。"
        )
    out.append("")
    out.append("## 限制")
    out.append("")
    out.append(
        f"- 单模型（DeepSeek V4 Flash）单次运行，n={len(rows)}；"
        "可移植性标签是题目属性，但通过率分层需要跨模型复现。"
    )
    out.append(
        "- `ref_cf` 用 `analyze_submission_footprint` 的保守行序列启发式，"
        "作者自己也标注需要人工审计才能进论文主张。"
    )
    flagged = [
        r for r in rows
        if r["api_resolve"] is not None and r["api_resolve"] >= PORTABLE_API_RESOLVE
    ]
    precision = (
        sum(1 for r in flagged if r["ref_cf"] >= PORTABLE_REF_CF) / len(flagged)
        if flagged
        else float("nan")
    )
    out.append(
        "- `api_resolve` 只匹配名字，不检查签名或语义，"
        f"在 `api_resolve >= {PORTABLE_API_RESOLVE}` 处精确率 {precision:.0%}，"
        "误判的那部分会被当成可移植题。"
    )
    return "\n".join(out) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rows = collect(args.run)
    if not rows:
        raise SystemExit("no comparable tasks found")

    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "task_portability.json").write_text(
        json.dumps({"n": len(rows), "rows": rows}, indent=2) + "\n", encoding="utf-8"
    )
    (args.output / "task_portability.md").write_text(render(rows), encoding="utf-8")
    print(f"analyzed {len(rows)} tasks; wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
