#!/usr/bin/env python3
"""Verification-loop description + Phase 3 AUC on existing gold trajectories.

Offline only. Does not write a stopping rule or change eval/result.json.
Label is earliest sufficient snapshot T* from Phase 1. Features are
runtime-legal signals computed from history at time t.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "harness"))

from featureliftbench.token_utility_signals import (  # noqa: E402
    INSPECT_CATS,
    LEGAL_FEATURE_KEYS,
    WINDOW_K,
    attach_action_features,
    attribute_tokens,
    classify_self_test_event,
    iter_gold_pass_reports,
    label_already_enough,
    load_paired_actions,
    mean_or_none,
    rate_or_none,
    roc_auc,
    zscore,
)

NEAR_CHANCE = 0.55
WEAK = 0.70


def _quantile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    pos = (len(ordered) - 1) * p
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi:
        return float(ordered[lo])
    return float(ordered[lo] + (ordered[hi] - ordered[lo]) * (pos - lo))


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _suite_label(suite: str) -> str:
    name = Path(suite).name
    if "deepseek-v4-flash" in suite and "python200" in name:
        return "flash_local_main200"
    if "qwen3.6-35b" in suite and "external50" in name and "main" in name:
        return "qwen35b_e50_main"
    if "qwen3.6-35b" in suite and "v1" in name:
        return "qwen35b_v1_200"
    return name


def _summarize_flags(rows: list[dict[str, Any]], keys: tuple[str, ...]) -> dict[str, Any]:
    if not rows:
        return {"n": 0}
    billed = sum(int(row.get("billed") or 0) for row in rows) or 1
    out: dict[str, Any] = {"n": len(rows), "billed": sum(int(row.get("billed") or 0) for row in rows)}
    for key in keys:
        flags = [bool(row.get(key)) for row in rows]
        out[f"rate_{key}"] = rate_or_none(flags)
        out[f"billed_share_{key}"] = (
            sum(int(row.get("billed") or 0) for row, flag in zip(rows, flags) if flag) / billed
        )
    return out


def verification_loop_task(
    *,
    actions: list[dict[str, Any]],
    unique: list[dict[str, Any]],
    t_star: int,
    total: int,
) -> dict[str, Any]:
    tests: list[dict[str, Any]] = []
    inspects: list[dict[str, Any]] = []
    for index, action in enumerate(actions):
        billed = int(action.get("billed") or 0)
        if action.get("cat") == "self_test_run":
            row = classify_self_test_event(
                action,
                t_star=t_star,
                unique=unique,
                actions=actions,
                index=index,
            )
            row["billed"] = billed
            tests.append(row)
        if action.get("cat") in INSPECT_CATS:
            inspects.append(
                {
                    "before_tstar": int(action.get("tokens") or 0) < t_star,
                    "path_novel": bool(action.get("path_novel")),
                    "billed": billed,
                }
            )
    pre = [row for row in tests if row["before_tstar"]]
    post = [row for row in tests if not row["before_tstar"]]
    pre_ins = [row for row in inspects if row["before_tstar"]]
    post_ins = [row for row in inspects if not row["before_tstar"]]
    flag_keys = (
        "cmd_novel",
        "out_novel",
        "pair_novel",
        "identical_rerun",
        "new_info",
        "followed_by_package_write",
        "followed_by_new_tree",
        "followed_by_new_tree_soon",
        "followed_by_new_tree_before_tstar",
        "useful_strict",
        "useful_loose",
    )
    cells_pre = Counter()
    cells_post = Counter()
    for row, bucket in ((row, cells_pre if row["before_tstar"] else cells_post) for row in tests):
        info = "new_info" if row["new_info"] else "no_new_info"
        tree = "new_tree" if row["followed_by_new_tree_soon"] else "no_new_tree"
        bucket[f"{info}|{tree}"] += 1
        if row["identical_rerun"]:
            bucket["identical_rerun"] += 1
    trees_before = sum(1 for item in unique if item.get("tokens") is not None and int(item["tokens"]) <= t_star)
    trees_after = sum(1 for item in unique if item.get("tokens") is not None and int(item["tokens"]) > t_star)
    return {
        "n_self_test": len(tests),
        "n_self_test_pre": len(pre),
        "n_self_test_post": len(post),
        "n_inspect_pre": len(pre_ins),
        "n_inspect_post": len(post_ins),
        "pre": _summarize_flags(pre, flag_keys),
        "post": _summarize_flags(post, flag_keys),
        "cells_pre": dict(cells_pre),
        "cells_post": dict(cells_post),
        "inspect_repeat_pre": (
            None
            if not pre_ins
            else 1.0 - (sum(1 for row in pre_ins if row["path_novel"]) / len(pre_ins))
        ),
        "inspect_repeat_post": (
            None
            if not post_ins
            else 1.0 - (sum(1 for row in post_ins if row["path_novel"]) / len(post_ins))
        ),
        "unique_trees_at_or_before_tstar": trees_before,
        "unique_trees_after_tstar": trees_after,
        "tail_frac": ((total - t_star) / total) if total else None,
    }


def _pool_loop(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"n_tasks": 0}

    def _mean_rate(split: str, key: str) -> float | None:
        vals = [
            (task[split] or {}).get(f"rate_{key}")
            for task in rows
            if (task[split] or {}).get("n")
        ]
        vals = [v for v in vals if v is not None]
        return mean_or_none(vals)

    def _pooled_share(split: str, key: str) -> float | None:
        billed = 0.0
        hit = 0.0
        for task in rows:
            block = task.get(split) or {}
            amount = float(block.get("billed") or 0)
            billed += amount
            share = block.get(f"billed_share_{key}")
            if share is None or amount <= 0:
                continue
            hit += float(share) * amount
        if billed <= 0:
            return None
        return hit / billed

    cells_pre: Counter[str] = Counter()
    cells_post: Counter[str] = Counter()
    for task in rows:
        cells_pre.update(task.get("cells_pre") or {})
        cells_post.update(task.get("cells_post") or {})
    n_pre = sum(task["n_self_test_pre"] for task in rows)
    n_post = sum(task["n_self_test_post"] for task in rows)
    return {
        "n_tasks": len(rows),
        "n_self_test_pre": n_pre,
        "n_self_test_post": n_post,
        "mean_n_self_test_pre": mean_or_none(task["n_self_test_pre"] for task in rows),
        "mean_n_self_test_post": mean_or_none(task["n_self_test_post"] for task in rows),
        "tasks_with_post_self_test": sum(task["n_self_test_post"] > 0 for task in rows) / len(rows),
        "pre_rate_new_info": _mean_rate("pre", "new_info"),
        "pre_rate_identical_rerun": _mean_rate("pre", "identical_rerun"),
        "pre_rate_useful_strict": _mean_rate("pre", "useful_strict"),
        "pre_rate_useful_loose": _mean_rate("pre", "useful_loose"),
        "pre_rate_new_tree_before_tstar": _mean_rate("pre", "followed_by_new_tree_before_tstar"),
        "pre_rate_new_tree_soon": _mean_rate("pre", "followed_by_new_tree_soon"),
        "post_rate_new_info": _mean_rate("post", "new_info"),
        "post_rate_identical_rerun": _mean_rate("post", "identical_rerun"),
        "post_rate_followed_by_new_tree": _mean_rate("post", "followed_by_new_tree"),
        "post_rate_followed_by_package_write": _mean_rate("post", "followed_by_package_write"),
        "pre_billed_share_identical_rerun": _pooled_share("pre", "identical_rerun"),
        "post_billed_share_identical_rerun": _pooled_share("post", "identical_rerun"),
        "pre_billed_share_useful_strict": _pooled_share("pre", "useful_strict"),
        "pre_billed_share_useful_loose": _pooled_share("pre", "useful_loose"),
        "mean_inspect_repeat_pre": mean_or_none(
            task["inspect_repeat_pre"] for task in rows if task.get("inspect_repeat_pre") is not None
        ),
        "mean_inspect_repeat_post": mean_or_none(
            task["inspect_repeat_post"] for task in rows if task.get("inspect_repeat_post") is not None
        ),
        "mean_unique_trees_after_tstar": mean_or_none(task["unique_trees_after_tstar"] for task in rows),
        "tasks_with_new_tree_after_tstar": sum(task["unique_trees_after_tstar"] > 0 for task in rows)
        / len(rows),
        "cells_pre": dict(cells_pre),
        "cells_post": dict(cells_post),
        "cells_pre_share": (
            {key: value / n_pre for key, value in cells_pre.items() if "|" in key} if n_pre else {}
        ),
        "cells_post_share": (
            {key: value / n_post for key, value in cells_post.items() if "|" in key} if n_post else {}
        ),
    }


def _feature_auc_table(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"n": 0}
    y = [int(row["already_enough"]) for row in rows]
    n_pos = sum(y)
    table: dict[str, Any] = {
        "n": len(rows),
        "n_already_enough": n_pos,
        "n_still_necessary": len(rows) - n_pos,
        "prevalence_already_enough": n_pos / len(rows),
        "features": {},
        "reference": {},
    }
    for key in LEGAL_FEATURE_KEYS:
        scores = [float(row["features"][key]) for row in rows]
        auc = roc_auc(y, scores)
        table["features"][key] = {
            "auc_already_enough": auc,
            "auc_best_direction": None if auc is None else max(auc, 1.0 - auc),
            "mean_before": mean_or_none(
                row["features"][key] for row in rows if row["already_enough"] == 0
            ),
            "mean_after": mean_or_none(
                row["features"][key] for row in rows if row["already_enough"] == 1
            ),
        }
    for key in ("tokens_so_far", "action_index", "unique_trees_so_far", "last_tree_n_bytes"):
        if key in ("tokens_so_far", "action_index"):
            scores = [float(row[key]) for row in rows]
        else:
            scores = [float(row["features"][key]) for row in rows]
        auc = roc_auc(y, scores)
        table["reference"][key] = {
            "auc_already_enough": auc,
            "auc_best_direction": None if auc is None else max(auc, 1.0 - auc),
            "note": "monotonic or size proxy; not a verification-loop signal",
        }
    keyed = list(LEGAL_FEATURE_KEYS)
    columns = {key: zscore([float(row["features"][key]) for row in rows]) for key in keyed}
    combo = [_z_combo({key: columns[key][i] for key in keyed}) for i in range(len(rows))]
    combo_auc = roc_auc(y, combo)
    table["combo_unfitted"] = {
        "auc_already_enough": combo_auc,
        "auc_best_direction": None if combo_auc is None else max(combo_auc, 1.0 - combo_auc),
        "note": "hypothesized signs, z-scored on this split; not a fitted stop rule",
    }
    return table


def _z_combo(zfeat: dict[str, float]) -> float:
    return (
        zfeat["consecutive_self_tests"]
        + zfeat["tokens_since_last_useful_write"]
        + zfeat["steps_since_last_useful_write"]
        + zfeat["repeat_command_rate"]
        + zfeat["repeat_read_rate"]
        - zfeat["frac_recent_self_test_out_novel"]
        - zfeat["self_test_out_novel"]
        - zfeat["recent_new_trees"]
    )


def _decision_hint(auc: float | None) -> str:
    if auc is None:
        return "insufficient_labels"
    if auc < NEAR_CHANCE:
        return "near_chance_stop_early_stopping"
    if auc < WEAK:
        return "weak_do_not_write_stop_rule"
    return "above_weak_threshold_still_no_stop_rule"


def _slice_rows(
    rows: list[dict[str, Any]],
    *,
    self_test_only: bool = False,
    token_lo: int | None = None,
    token_hi: int | None = None,
    min_tokens: int | None = None,
) -> list[dict[str, Any]]:
    out = rows
    if self_test_only:
        out = [row for row in out if row.get("cat") == "self_test_run"]
    if min_tokens is not None:
        out = [row for row in out if int(row["tokens_so_far"]) >= min_tokens]
    if token_lo is not None:
        out = [row for row in out if int(row["tokens_so_far"]) >= token_lo]
    if token_hi is not None:
        out = [row for row in out if int(row["tokens_so_far"]) <= token_hi]
    return out


def build_call_rows(
    *,
    calls: list[tuple[float, int, int]],
    actions: list[dict[str, Any]],
    t_star: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    ai = 0
    last_feat: dict[str, float] | None = None
    last_idx = -1
    last_cat = None
    for ts, _billed, cum in calls:
        while (
            ai < len(actions)
            and actions[ai].get("ts") is not None
            and float(actions[ai]["ts"]) <= ts + 1.0
        ):
            last_feat = actions[ai].get("features")
            last_idx = ai
            last_cat = actions[ai].get("cat")
            ai += 1
        if not last_feat:
            continue
        y = label_already_enough(int(cum), t_star)
        if y is None:
            continue
        rows.append(
            {
                "already_enough": y,
                "still_necessary": 1 - y,
                "features": last_feat,
                "tokens_so_far": int(cum),
                "action_index": last_idx,
                "cat": last_cat,
                "source": "call",
            }
        )
    return rows


def build_phase3_rows(
    *,
    actions: list[dict[str, Any]],
    t_star: int,
    source: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, action in enumerate(actions):
        tokens = action.get("tokens")
        y = label_already_enough(tokens, t_star)
        if y is None or action.get("features") is None:
            continue
        rows.append(
            {
                "already_enough": y,
                "still_necessary": 1 - y,
                "features": action["features"],
                "tokens_so_far": int(tokens or 0),
                "action_index": index,
                "cat": action.get("cat"),
                "source": source,
            }
        )
    return rows


def analyze_suite(
    *,
    suite: str,
    reports: list[tuple[dict[str, Any], dict[str, Any]]],
    limit: int | None = None,
) -> dict[str, Any]:
    loop_rows: list[dict[str, Any]] = []
    action_rows: list[dict[str, Any]] = []
    call_rows: list[dict[str, Any]] = []
    skipped = 0
    for report, summary in reports[: limit or None]:
        task_id = report["task_id"]
        t_star = int(summary["earliest_pass_tokens"])
        total = int(summary.get("total_tokens") or report.get("total_tokens") or 0)
        task_dir = Path(suite) / task_id
        if not (task_dir / "agent" / "openhands_events.jsonl").is_file():
            skipped += 1
            continue
        calls, actions = load_paired_actions(task_dir)
        unique = list(report.get("unique") or [])
        attach_action_features(actions, unique=unique, window_k=WINDOW_K)
        attribute_tokens(calls, actions)
        loop = verification_loop_task(actions=actions, unique=unique, t_star=t_star, total=total)
        loop["task_id"] = task_id
        loop["t_star"] = t_star
        loop["total_tokens"] = total
        loop_rows.append(loop)
        action_rows.extend(build_phase3_rows(actions=actions, t_star=t_star, source="action"))
        call_rows.extend(build_call_rows(calls=calls, actions=actions, t_star=t_star))
    slices = {
        "all_actions": _feature_auc_table(action_rows),
        "self_test_actions": _feature_auc_table(_slice_rows(action_rows, self_test_only=True)),
        "billed_calls": _feature_auc_table(call_rows),
        "warmup_ge_50k": _feature_auc_table(_slice_rows(action_rows, min_tokens=50_000)),
        "token_band_500k_1500k": _feature_auc_table(
            _slice_rows(action_rows, token_lo=500_000, token_hi=1_500_000)
        ),
    }
    combo_auc = (slices["all_actions"].get("combo_unfitted") or {}).get("auc_already_enough")
    band_auc = (slices["token_band_500k_1500k"].get("combo_unfitted") or {}).get("auc_already_enough")
    call_auc = (slices["billed_calls"].get("combo_unfitted") or {}).get("auc_already_enough")
    band_best = (slices["token_band_500k_1500k"].get("combo_unfitted") or {}).get("auc_best_direction")
    return {
        "suite": suite,
        "label": _suite_label(suite),
        "n_gold_pass": len(loop_rows),
        "skipped_missing_events": skipped,
        "window_k": WINDOW_K,
        "verification_loop": _pool_loop(loop_rows),
        "phase3": {
            "label": "already_enough = 1 if t >= T*",
            "legal_features": list(LEGAL_FEATURE_KEYS),
            "slices": slices,
            "combo_auc_all_actions": combo_auc,
            "combo_auc_billed_calls": call_auc,
            "combo_auc_token_band_500k_1500k": band_auc,
            "combo_auc_best_direction_token_band": band_best,
            "decision_hint_all_actions": _decision_hint(combo_auc),
            "decision_hint_billed_calls": _decision_hint(call_auc),
            "decision_hint_token_band": _decision_hint(band_auc),
            "note": (
                "Token-band AUC is the real test: same spend, some tasks already "
                "past T*, some not. All-actions AUC can be a late-vs-early proxy. "
                "tokens_so_far is a reference baseline, not a verification signal. "
                "No stopping rule is emitted."
            ),
        },
        "tasks": [
            {
                "task_id": row["task_id"],
                "t_star": row["t_star"],
                "n_self_test_pre": row["n_self_test_pre"],
                "n_self_test_post": row["n_self_test_post"],
                "pre": row["pre"],
                "post": row["post"],
                "inspect_repeat_pre": row["inspect_repeat_pre"],
                "inspect_repeat_post": row["inspect_repeat_post"],
                "unique_trees_after_tstar": row["unique_trees_after_tstar"],
            }
            for row in loop_rows
        ],
    }


def _print_suite(block: dict[str, Any]) -> None:
    loop = block["verification_loop"]
    phase3 = block["phase3"]
    print(f"== {block['label']}  n_gold_pass={block['n_gold_pass']} ==")
    print(
        f"  self-tests pre={loop.get('n_self_test_pre')} post={loop.get('n_self_test_post')}  "
        f"tasks with post self-test={loop.get('tasks_with_post_self_test')}"
    )
    print(
        f"  pre new_info={loop.get('pre_rate_new_info')}  "
        f"identical_rerun={loop.get('pre_rate_identical_rerun')}  "
        f"useful_strict={loop.get('pre_rate_useful_strict')}  "
        f"useful_loose={loop.get('pre_rate_useful_loose')}"
    )
    print(
        f"  post new_info={loop.get('post_rate_new_info')}  "
        f"identical_rerun={loop.get('post_rate_identical_rerun')}  "
        f"new_tree={loop.get('post_rate_followed_by_new_tree')}"
    )
    print(
        f"  inspect repeat pre={loop.get('mean_inspect_repeat_pre')}  "
        f"post={loop.get('mean_inspect_repeat_post')}"
    )
    all_act = phase3["slices"]["all_actions"]
    band = phase3["slices"]["token_band_500k_1500k"]
    print(
        f"  AUC combo all-actions={phase3.get('combo_auc_all_actions')}  "
        f"n={all_act.get('n')}  hint={phase3.get('decision_hint_all_actions')}"
    )
    print(
        f"  AUC combo token-band 0.5-1.5M={phase3.get('combo_auc_token_band_500k_1500k')}  "
        f"n={band.get('n')}  hint={phase3.get('decision_hint_token_band')}"
    )
    ref = (all_act.get("reference") or {}).get("tokens_so_far") or {}
    print(f"  reference tokens_so_far AUC={ref.get('auc_already_enough')}")
    feats = all_act.get("features") or {}
    ranked = sorted(
        feats.items(),
        key=lambda kv: -((kv[1] or {}).get("auc_best_direction") or 0),
    )
    for key, info in ranked[:6]:
        print(
            f"    {key:34} auc={info.get('auc_already_enough')}  "
            f"best={info.get('auc_best_direction')}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase1", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--label-filter", default="", help="Substring filter on suite path")
    parser.add_argument("--limit", type=int, default=0, help="Per-suite task cap (debug)")
    args = parser.parse_args()
    phase1 = _load_json(args.phase1)
    grouped: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = {}
    for suite, report, summary in iter_gold_pass_reports(phase1):
        if args.label_filter and args.label_filter not in suite:
            continue
        grouped.setdefault(suite, []).append((report, summary))
    blocks = []
    for suite, reports in grouped.items():
        print(f"analyzing {suite} n={len(reports)}", flush=True)
        block = analyze_suite(
            suite=suite,
            reports=reports,
            limit=args.limit or None,
        )
        _print_suite(block)
        blocks.append(block)
    slim = []
    for block in blocks:
        slim.append(
            {
                "suite": block["suite"],
                "label": block["label"],
                "n_gold_pass": block["n_gold_pass"],
                "verification_loop": block["verification_loop"],
                "phase3": {
                    key: value
                    for key, value in block["phase3"].items()
                    if key != "slices"
                }
                | {"slices": block["phase3"]["slices"]},
            }
        )
    _write_json(
        args.output,
        {
            "phase1": str(args.phase1),
            "not_a_stopping_rule": True,
            "blocks": slim,
            "tasks": [
                {"suite": block["suite"], "label": block["label"], "tasks": block["tasks"]}
                for block in blocks
            ],
        },
    )
    print("wrote", args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
