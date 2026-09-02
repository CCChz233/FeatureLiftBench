#!/usr/bin/env python3
"""Offline calibration for portability-gated early stopping.

The unstratified stall terminator was killed because it truncated runs before
any passing tree existed.  That calibration pooled every task.  This script
tests whether the loss is concentrated in tasks where the declared API has no
coherent upstream counterpart, i.e. where the agent genuinely has to synthesise
rather than transplant.

Portability is labelled two ways:

``ref_cf``
    Copy fraction of the *reference solution* against the pinned ``repo/``.
    Oracle-derived, so it is a ground-truth label only and can never be used at
    agent runtime.

``api_resolve``
    Fraction of ``public_spec.required_api`` leaf names that resolve to a
    definition in the pinned ``repo/``.  Computed from task inputs alone, so it
    is the deployable gate.

Savings are reported against the full suite token budget, because non-portable
tasks are left untouched by the rule.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from audit_contract_entailment import index_upstream  # noqa: E402
from calibrate_vct_stall import fire_point, gold_passing, load_tasks  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]

K_GRID = [100_000, 150_000, 200_000, 250_000, 300_000, 400_000, 500_000]
FLOOR_GRID = [0, 250_000, 500_000, 750_000, 1_000_000, 1_500_000, 2_000_000]

PORTABLE_REF_CF = 0.90
PORTABLE_API_RESOLVE = 0.99


def _task_dir(task_id: str) -> Path | None:
    for parent in ("benchmark/tasks", "benchmark/python200_hard_tasks"):
        candidate = ROOT / parent / task_id
        if candidate.is_dir():
            return candidate
    return None


def api_resolve(task: Path) -> float | None:
    """Fraction of declared API leaf names that exist in the pinned repo."""
    try:
        metadata = json.loads((task / "metadata.json").read_text(encoding="utf-8"))
    except Exception:
        return None
    required = (metadata.get("public_spec") or {}).get("required_api") or []
    if not required:
        return None
    try:
        index = index_upstream(task / "repo")
    except Exception:
        return None
    names = set(index)
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


def reference_copy_fraction(task: Path) -> float | None:
    oracle = ROOT / "benchmark" / "submissions" / task.name / "oracle"
    if not oracle.is_dir():
        return None
    from featureliftbench.compactness import analyze_submission_footprint

    try:
        vector = analyze_submission_footprint(task, oracle, reference_path=oracle)
    except Exception:
        return None
    value = vector.get("copied_fraction")
    return float(value) if value is not None else None


def label_tasks(tasks: list[dict[str, Any]]) -> dict[str, dict[str, float | None]]:
    labels: dict[str, dict[str, float | None]] = {}
    for task in tasks:
        task_id = str(task.get("task_id") or task.get("task") or "")
        if not task_id or task_id in labels:
            continue
        directory = _task_dir(task_id)
        if directory is None:
            labels[task_id] = {"ref_cf": None, "api_resolve": None}
            continue
        labels[task_id] = {
            "ref_cf": reference_copy_fraction(directory),
            "api_resolve": api_resolve(directory),
        }
    return labels


def evaluate(
    tasks: list[dict[str, Any]],
    labels: dict[str, dict[str, float | None]],
    k: int,
    floor: int,
    *,
    gate: str | None,
    suite_total: int,
) -> dict[str, Any]:
    """Run the stall rule, firing only on tasks the gate admits."""
    saved_tokens = 0
    fired = 0
    gated_out = 0
    pass_lost_before = 0
    pass_lost_after = 0
    undecided = 0
    stop_over_tstar: list[float] = []

    for task in tasks:
        task_id = str(task.get("task_id") or task.get("task") or "")
        label = labels.get(task_id) or {}
        if gate is not None:
            threshold = PORTABLE_REF_CF if gate == "ref_cf" else PORTABLE_API_RESOLVE
            value = label.get(gate)
            if value is None or value < threshold:
                gated_out += 1
                continue

        trees = sorted(task["unique"], key=lambda t: t["tokens"])
        total = int(task.get("total_tokens") or 0)
        if total <= 0:
            continue
        shot = fire_point(trees, total, k, floor)
        if shot is None:
            continue
        stop, index = shot
        fired += 1
        saved_tokens += total - stop

        summary = task.get("summary") or {}
        earliest = summary.get("earliest_pass_tokens")
        if earliest is not None and int(earliest):
            stop_over_tstar.append(stop / int(earliest))
        if earliest is not None and stop < int(earliest):
            pass_lost_before += 1
            continue

        held = trees[index]["tree_hash"]
        evaluated = {
            snapshot["tree_hash"]: snapshot
            for snapshot in (task.get("snapshots") or [])
            if snapshot.get("evaled")
        }
        record = evaluated.get(held)
        if record is None:
            undecided += 1
        elif float(record.get("functional_gate") or 0.0) != 1.0:
            pass_lost_after += 1

    return {
        "k": k,
        "floor": floor,
        "gate": gate or "none",
        "eligible": len(tasks) - gated_out,
        "fired": fired,
        "saved_tokens": saved_tokens,
        "saved_suite": saved_tokens / suite_total if suite_total else 0.0,
        "pass_lost": pass_lost_before + pass_lost_after,
        "pass_lost_before_tstar": pass_lost_before,
        "pass_lost_after_tstar": pass_lost_after,
        "undecided": undecided,
        "stop_over_tstar_median": (
            statistics.median(stop_over_tstar) if stop_over_tstar else 0.0
        ),
    }


def render(
    rows: list[dict[str, Any]],
    labels: dict[str, dict[str, float | None]],
    n_tasks: int,
    suite_total: int,
) -> str:
    out = ["# 可移植性门控的早停：离线标定", ""]
    out.append("> **Status: AI 生成的离线标定 · 未跑任何模型**")
    out.append("")
    out.append("## 为什么要分层")
    out.append("")
    out.append(
        "未分层的 stall 终止已经被否决：它把运行截断在最早通过树之前。"
        "那次标定把所有题混在一起。本测试检验丢分是否集中在"
        "**声明 API 在上游没有对应实现**的题上——也就是 Agent 必须自己合成、"
        "而不是移植的那些题。"
    )
    out.append("")
    labelled = [
        v for v in labels.values() if v.get("ref_cf") is not None
    ]
    portable = [v for v in labelled if (v["ref_cf"] or 0) >= PORTABLE_REF_CF]
    out.append(
        f"金标共 **{n_tasks}** 道通过题，其中 {len(labelled)} 道能算出参考解抄袭度，"
        f"{len(portable)} 道判为可移植（`ref_cf >= {PORTABLE_REF_CF}`）。"
    )
    out.append("")
    out.append("## 网格")
    out.append("")
    out.append(
        "| 门控 | K | FLOOR | 触发 | 全套节省 | 丢 pass | 停在 T\\* 前 "
        "| 停在坏树上 | 不可判定 | stop/T\\* 中位 |"
    )
    out.append("| :-- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for row in rows:
        out.append(
            f"| {row['gate']} | {row['k'] // 1000}K | {row['floor'] // 1000}K "
            f"| {row['fired']} | {row['saved_suite']:.1%} | {row['pass_lost']} "
            f"| **{row['pass_lost_before_tstar']}** | {row['pass_lost_after_tstar']} "
            f"| {row['undecided']} | {row['stop_over_tstar_median']:.2f} |"
        )
    out.append("")
    out.append("## 判定")
    out.append("")
    clean = [r for r in rows if r["gate"] != "none" and r["pass_lost"] == 0]
    if clean:
        best = max(clean, key=lambda r: r["saved_suite"])
        out.append(
            f"存在零丢分的网格点。最好的是 `{best['gate']}` 门控、"
            f"K={best['k'] // 1000}K / FLOOR={best['floor'] // 1000}K："
            f"全套节省 **{best['saved_suite']:.1%}**，触发 {best['fired']} 题，"
            f"丢 pass 0，不可判定 {best['undecided']}。"
        )
    else:
        out.append(
            "**没有任何门控网格点做到零丢分。** 可移植性门控没有把 T\\* 前截断消掉，"
            "早停在本套件上不成立。"
        )
    out.append("")
    out.append("## 限制")
    out.append("")
    out.append(
        "- 节省分母是金标通过题的 token 合计；失败题被规则截断同样省 token 且不丢分，"
        "所以真实节省高于此处。"
    )
    out.append(
        "- 去掉了 VCT 的结构 Gate 合取项。加回它只会推迟停止、减少节省，"
        "但也可能救回 `停在坏树上` 的那一类。"
    )
    out.append("- 只有 Flash 一个模型的金标，跨模型必须重标定。")
    return "\n".join(out) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase1", type=Path, nargs="+")
    parser.add_argument(
        "--suite-filter", default="python200-deepseek-v4-flash-vllm-local-0812-001"
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    tasks = gold_passing(load_tasks(args.phase1, args.suite_filter))
    if not tasks:
        raise SystemExit("no gold passing tasks matched the suite filter")

    labels = label_tasks(tasks)
    suite_total = sum(int(t.get("total_tokens") or 0) for t in tasks)

    rows = []
    for gate in (None, "ref_cf", "api_resolve"):
        for floor in FLOOR_GRID:
            for k in K_GRID:
                rows.append(
                    evaluate(
                        tasks, labels, k, floor, gate=gate, suite_total=suite_total
                    )
                )

    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "portability_gated_stop.json").write_text(
        json.dumps(
            {
                "n_tasks": len(tasks),
                "suite_total_tokens": suite_total,
                "labels": labels,
                "grid": rows,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (args.output / "portability_gated_stop.md").write_text(
        render(rows, labels, len(tasks), suite_total), encoding="utf-8"
    )
    print(f"calibrated {len(rows)} grid points on {len(tasks)} gold passing tasks")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
