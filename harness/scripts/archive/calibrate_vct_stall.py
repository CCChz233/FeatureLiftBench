#!/usr/bin/env python3
"""One-sided offline kill test for the VCT stall terminator.

VCT terminates a run when three facts hold at once: an absolute token floor is
reached, the structural contract gate is closed on the current submission tree,
and no new unique tree has appeared for K tokens. Calibrating the full rule
needs the tree contents so the gate can be recomputed, and those live with the
original trajectories rather than in the published analysis JSON.

This script calibrates the rule with the gate conjunct *dropped*. Because the
gate is an additional conjunct, requiring it can only postpone the stop, which
can only reduce the token savings. The savings measured here are therefore an
upper bound on what the full rule can achieve, so a shortfall is decisive: if
the stall-only rule cannot reach the target savings, neither can VCT.

Pass loss is not bounded the same way and is reported for direction only, split
into what the data can and cannot decide.
"""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

DEFAULT_K = [100_000, 150_000, 200_000, 250_000, 300_000, 400_000, 500_000]
DEFAULT_FLOOR = [0, 250_000, 500_000, 750_000, 1_000_000, 1_500_000, 2_000_000]

# Savings target from the VCT spec's offline kill gate.
TARGET_SAVED = 0.25
TARGET_PASS_LOST = 1


def load_tasks(paths: list[Path], suite_filter: str | None) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        for report in payload.get("reports") or []:
            suite = str(report.get("suite", ""))
            if suite_filter and suite_filter not in suite:
                continue
            for task in report.get("reports") or []:
                task = dict(task)
                task["_suite"] = suite
                tasks.append(task)
    return tasks


def gold_passing(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Tasks whose replay matched and where some evaluated tree passed."""
    out = []
    for task in tasks:
        if not task.get("replay_ok"):
            continue
        summary = task.get("summary") or {}
        if summary.get("earliest_pass_tokens") is None:
            continue
        if not task.get("unique"):
            continue
        out.append(task)
    return out


def fire_point(trees: list[dict[str, Any]], total: int, k: int, floor: int) -> tuple[int, int] | None:
    """First (stop_tokens, tree_index) where the stall rule fires, if it does.

    A stop can only happen inside a gap between consecutive unique trees, or in
    the tail after the last one.
    """
    for position, tree in enumerate(trees):
        start = int(tree["tokens"])
        boundary = int(trees[position + 1]["tokens"]) if position + 1 < len(trees) else total
        candidate = max(start + k, floor)
        if candidate < boundary:
            return candidate, position
    return None


def evaluate(
    tasks: list[dict[str, Any]], k: int, floor: int
) -> dict[str, Any]:
    saved_fracs: list[float] = []
    pass_lost_before = 0
    pass_lost_after = 0
    undecided = 0
    never_fired = 0
    late_truncated = 0
    saved_tokens = 0
    total_tokens = 0
    stop_over_tstar: list[float] = []

    for task in tasks:
        trees = sorted(task["unique"], key=lambda t: t["tokens"])
        total = int(task.get("total_tokens") or 0)
        if total <= 0:
            continue
        summary = task.get("summary") or {}
        earliest = summary.get("earliest_pass_tokens")
        total_tokens += total

        shot = fire_point(trees, total, k, floor)
        if shot is None:
            never_fired += 1
            continue
        stop, index = shot
        saved_fracs.append((total - stop) / total)
        saved_tokens += total - stop

        if earliest is not None:
            stop_over_tstar.append(stop / int(earliest) if int(earliest) else 0.0)

        # A stop before the earliest passing tree loses the pass by definition.
        # No structural gate can rescue these: surface completeness is reached
        # long before behavioral correctness, so the gate is already closed.
        if earliest is not None and stop < int(earliest):
            pass_lost_before += 1
            if summary.get("late_pass"):
                late_truncated += 1
            continue

        # Otherwise the verdict depends on whether the tree held at the stop was
        # evaluated; a later edit can break an already passing package.
        held = trees[index]["tree_hash"]
        evaled = {
            s["tree_hash"]: s
            for s in (task.get("snapshots") or [])
            if s.get("evaled")
        }
        record = evaled.get(held)
        if record is None:
            undecided += 1
        elif float(record.get("functional_gate") or 0.0) != 1.0:
            pass_lost_after += 1

    return {
        "k": k,
        "floor": floor,
        "n": len(tasks),
        "fired": len(saved_fracs),
        "never_fired": never_fired,
        "saved_median": statistics.median(saved_fracs) if saved_fracs else 0.0,
        "saved_pooled": saved_tokens / total_tokens if total_tokens else 0.0,
        "pass_lost": pass_lost_before + pass_lost_after,
        "pass_lost_before_tstar": pass_lost_before,
        "pass_lost_after_tstar": pass_lost_after,
        "undecided": undecided,
        "late_truncated": late_truncated,
        "stop_over_tstar_median": statistics.median(stop_over_tstar) if stop_over_tstar else 0.0,
    }


def render(rows: list[dict[str, Any]], n: int) -> str:
    out = ["# VCT stall 终止：离线单边否决测试", ""]
    out.append("> **Status: AI 生成的离线标定 · 上界测试 · 未跑任何模型**")
    out.append("")
    out.append("## 测试逻辑")
    out.append("")
    out.append(
        "VCT 的停止条件是三个事实同时成立：到达绝对 token 下限、当前提交树的结构"
        "契约 Gate 闭合、且此后 K 个 token 内没有新的独特树。完整标定需要逐棵树"
        "重算 Gate，而那需要树的内容，内容在原始轨迹里，不在已发布的分析 JSON 中。"
    )
    out.append("")
    out.append(
        "本测试**去掉 Gate 这一项**。Gate 是一个额外的合取项，要求它只会推迟停止，"
        "也就只会减少节省。因此这里量到的节省是 VCT 的**上界**：达不到目标就是决定"
        "性的否决，加回 Gate 只会更差。"
    )
    out.append("")
    out.append(
        f"分母是 Phase 1 金标里有最早通过树的 **{n}** 道通过题。"
        f"否决线取自 VCT 规格：节省 ≥ {TARGET_SAVED:.0%} 且丢失 pass ≤ {TARGET_PASS_LOST}。"
    )
    out.append("")
    out.append("## 网格")
    out.append("")
    out.append(
        "| K | FLOOR | 触发 | 节省合计 | 丢 pass | 其中 停在 T\\* 前 | 其中 停在坏树上 "
        "| 不可判定 | stop/T\\* 中位 |"
    )
    out.append("| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for row in rows:
        out.append(
            f"| {row['k'] // 1000}K | {row['floor'] // 1000}K | {row['fired']} "
            f"| {row['saved_pooled']:.1%} | {row['pass_lost']} "
            f"| **{row['pass_lost_before_tstar']}** | {row['pass_lost_after_tstar']} "
            f"| {row['undecided']} | {row['stop_over_tstar_median']:.2f} |"
        )
    out.append("")
    out.append(
        "`停在 T* 前` 是关键列：这些题在停止时刻**还不存在**任何能过的树。"
        "结构 Gate 救不了它们——`required_api` 的面在骨架阶段就闭合了，"
        "远早于行为正确。Gate 只能挡住 `停在坏树上` 那一类。"
    )
    out.append("")

    best = max(rows, key=lambda r: r["saved_pooled"])
    feasible = [
        r for r in rows
        if r["saved_pooled"] >= TARGET_SAVED and r["pass_lost"] <= TARGET_PASS_LOST
    ]
    out.append("## 判定")
    out.append("")
    out.append(
        f"节省上界出现在 K={best['k'] // 1000}K / FLOOR={best['floor'] // 1000}K："
        f"合计 **{best['saved_pooled']:.1%}**，中位 {best['saved_median']:.1%}，"
        f"同时丢 {best['pass_lost']} 道 pass、{best['undecided']} 道不可判定。"
    )
    out.append("")
    if best["saved_pooled"] < TARGET_SAVED:
        out.append(
            f"**否决。** 连去掉 Gate 的上界都拿不到 {TARGET_SAVED:.0%}，"
            "加回 Gate 只会推迟停止、进一步减少节省。VCT 的 token 主张不成立。"
        )
    elif not feasible:
        out.append(
            f"**上界可达 {TARGET_SAVED:.0%}，但没有任何 (K, FLOOR) 同时满足"
            f"丢 pass ≤ {TARGET_PASS_LOST}。** 需要 Gate 把这些提前停止挡掉才可能可行，"
            "因此必须做完整的 Gate 感知标定才能定论，不能凭本表放行。"
        )
    else:
        out.append(
            f"**上界通过。** {len(feasible)} 个网格点同时满足节省 ≥ {TARGET_SAVED:.0%} "
            f"且丢 pass ≤ {TARGET_PASS_LOST}："
        )
        out.append("")
        for row in feasible:
            out.append(
                f"- K={row['k'] // 1000}K / FLOOR={row['floor'] // 1000}K："
                f"节省 {row['saved_pooled']:.1%}，丢 {row['pass_lost']}，"
                f"不可判定 {row['undecided']}"
            )
        out.append("")
        out.append(
            "这**不是**放行结论。Gate 会推迟停止，真实节省低于此处；"
            "`不可判定` 的题需要补评那一刻持有的树才能定 `pass_lost`。"
        )
    out.append("")

    # The gate can only rescue stops that landed on a broken post-T* tree.
    at_target = [r for r in rows if r["saved_pooled"] >= TARGET_SAVED]
    if at_target:
        cheapest = min(at_target, key=lambda r: r["pass_lost"])
        out.append("## Gate 能救多少")
        out.append("")
        out.append(
            f"在所有达到 {TARGET_SAVED:.0%} 节省的网格点中，丢 pass 最少的是 "
            f"K={cheapest['k'] // 1000}K / FLOOR={cheapest['floor'] // 1000}K："
            f"丢 {cheapest['pass_lost']} 道，其中 **{cheapest['pass_lost_before_tstar']} 道停在 "
            f"T\\* 之前**、{cheapest['pass_lost_after_tstar']} 道停在过关后被改坏的树上。"
        )
        out.append("")
        out.append(
            f"结构 Gate 最多只能救回后者。即使它把 {cheapest['pass_lost_after_tstar']} 道全救回，"
            f"仍有 **{cheapest['pass_lost_before_tstar']}/{cheapest['n']}** 道 pass 被截断，"
            "远超非劣要求。"
        )
        out.append("")
    out.append("## 限制")
    out.append("")
    out.append(
        "- 只有 Flash 一个模型的金标。`TOKEN_UTILITY.md` 要求按模型分层，"
        "跨模型必须重标定。"
    )
    out.append(
        "- `不可判定` 来自停止时刻持有的树未被 docker 评测过；"
        "Phase 1 对通过题只抽样评测，不是全树评测。"
    )
    out.append(
        "- 停止早于最早通过树的题直接记为丢 pass，这一项是确定的，不依赖抽样。"
    )
    return "\n".join(out) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase1", type=Path, nargs="+", help="token_utility_phase1 JSON")
    parser.add_argument("--suite-filter", default="python200-deepseek-v4-flash-vllm-local-0812-001")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    tasks = gold_passing(load_tasks(args.phase1, args.suite_filter))
    if not tasks:
        raise SystemExit("no gold passing tasks matched the suite filter")

    rows = [
        evaluate(tasks, k, floor)
        for floor in DEFAULT_FLOOR
        for k in DEFAULT_K
    ]

    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "vct_stall_calibration.json").write_text(
        json.dumps({"n_tasks": len(tasks), "grid": rows}, indent=2) + "\n",
        encoding="utf-8",
    )
    (args.output / "vct_stall_calibration.md").write_text(
        render(rows, len(tasks)), encoding="utf-8"
    )
    print(f"calibrated {len(rows)} grid points on {len(tasks)} gold passing tasks")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
