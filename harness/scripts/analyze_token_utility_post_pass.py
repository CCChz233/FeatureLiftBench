#!/usr/bin/env python3
"""Classify billed tokens after Functional Pass (or after last package write).

Offline analysis. Does not change original eval/result.json.
Uses the same ActionEvent classifier as the Flash 2026-08-18 post-pass snapshot.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "harness"))

from featureliftbench.token_utility_replay import (  # noqa: E402
    load_billed_calls,
    parse_ts,
    tokens_at,
)
from featureliftbench.token_utility_signals import (  # noqa: E402
    CATS,
    action_fields,
    classify,
)


def _quantile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    pos = (len(ordered) - 1) * p
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi:
        return float(ordered[lo])
    return float(ordered[lo] + (ordered[hi] - ordered[lo]) * (pos - lo))


def load_actions(task_dir: Path) -> tuple[list[tuple[float, int, int]], list[dict[str, Any]]]:
    events_path = task_dir / "agent" / "openhands_events.jsonl"
    audit_path = task_dir / "agent" / "context_audit.jsonl"
    calls = load_billed_calls(audit_path)
    actions: list[dict[str, Any]] = []
    if not events_path.is_file():
        return calls, actions
    for line in events_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("kind") != "ActionEvent":
            continue
        ts = parse_ts(ev.get("timestamp"))
        tok = tokens_at(calls, ts)
        tool, command, path, summary = action_fields(ev)
        actions.append(
            {
                "ts": ts,
                "tokens": tok,
                "cat": classify(tool, command, path, summary),
                "tool": tool,
                "command": command,
                "summary": summary,
            }
        )
    return calls, actions


def attribute_tail(
    *,
    calls: list[tuple[float, int, int]],
    actions: list[dict[str, Any]],
    cutoff: int,
    total: int,
) -> dict[str, Any]:
    tail = max(0, total - cutoff)
    token_by = Counter()
    for i, call in enumerate(calls):
        ts, billed, cum = call
        if cum <= cutoff:
            continue
        prev = calls[i - 1][2] if i else 0
        portion = billed if prev >= cutoff else max(0, cum - cutoff)
        nxt = next((a for a in actions if a["ts"] is not None and a["ts"] >= ts - 0.05), None)
        if nxt and nxt["tokens"] is not None and nxt["tokens"] <= cutoff:
            nxt = next(
                (
                    a
                    for a in actions
                    if a["ts"] is not None
                    and a["ts"] >= ts - 0.05
                    and a["tokens"] is not None
                    and a["tokens"] > cutoff
                ),
                None,
            )
        if nxt is None:
            token_by["finish"] += portion
        else:
            token_by[nxt["cat"]] += portion
    post = [a for a in actions if a["tokens"] is not None and a["tokens"] > cutoff]
    act = Counter(a["cat"] for a in post)
    return {
        "cutoff": cutoff,
        "total": total,
        "tail": tail,
        "tail_frac": (tail / total) if total else None,
        "n_post": len(post),
        "act": dict(act),
        "tok": dict(token_by),
        "has_self_test": act.get("self_test_run", 0) + act.get("self_test_write", 0) > 0,
        "has_package_write": act.get("package_write", 0) > 0,
        "has_inspect_repo": act.get("inspect_repo", 0) + act.get("inspect_upstream_tests", 0) > 0,
        "has_upstream_tests": act.get("inspect_upstream_tests", 0) > 0,
    }


def summarize_rows(rows: list[dict[str, Any]], *, label: str) -> dict[str, Any]:
    if not rows:
        return {"label": label, "n": 0}
    pooled = Counter()
    actp = Counter()
    for row in rows:
        for key, value in row["tok"].items():
            pooled[key] += value
        for key, value in row["act"].items():
            actp[key] += value
    tail_sum = sum(row["tail"] for row in rows) or 1
    ok = [row for row in rows if row["tail"] >= 50_000]
    pooled_share = {key: value / tail_sum for key, value in pooled.items()}
    self_test_share = pooled.get("self_test_run", 0) + pooled.get("self_test_write", 0)
    inspect_share = sum(
        pooled.get(key, 0)
        for key in (
            "inspect_repo",
            "inspect_upstream_tests",
            "inspect_submission",
            "inspect_spec",
        )
    )
    tails = [row["tail"] for row in rows]
    fracs = [row["tail_frac"] for row in rows if row["tail_frac"] is not None]
    return {
        "label": label,
        "n": len(rows),
        "tail_median": statistics.median(tails),
        "tail_p25": _quantile(tails, 0.25),
        "tail_p90": _quantile(tails, 0.90),
        "tail_frac_median": statistics.median(fracs) if fracs else None,
        "tail_frac_p25": _quantile(fracs, 0.25),
        "tail_frac_p90": _quantile(fracs, 0.90),
        "total_median": statistics.median(row["total"] for row in rows),
        "cutoff_median": statistics.median(row["cutoff"] for row in rows),
        "pooled_tokens": dict(pooled),
        "pooled_share": pooled_share,
        "pooled_self_test_share": self_test_share / tail_sum,
        "pooled_inspect_share": inspect_share / tail_sum,
        "pooled_package_write_share": pooled.get("package_write", 0) / tail_sum,
        "pooled_actions": dict(actp),
        "n_tail_ge_50k": len(ok),
        "rates": {
            "has_self_test": sum(row["has_self_test"] for row in rows) / len(rows),
            "has_package_write": sum(row["has_package_write"] for row in rows) / len(rows),
            "has_inspect_repo": sum(row["has_inspect_repo"] for row in rows) / len(rows),
            "has_upstream_tests": sum(row.get("has_upstream_tests", False) for row in rows) / len(rows),
            "kept_mutating": sum(bool(row.get("kept_mutating")) for row in rows) / len(rows),
            "tail_ge_1m": sum(row["tail"] >= 1_000_000 for row in rows) / len(rows),
            "tail_frac_ge_50": sum((row["tail_frac"] or 0) >= 0.5 for row in rows) / len(rows),
        },
        "mean_tail_share_ge_50k": {
            cat: statistics.mean(row["tok"].get(cat, 0) / row["tail"] for row in ok)
            for cat in CATS
            if ok
        }
        if ok
        else {},
    }


def analyze_phase1_suite(
    payload: dict[str, Any],
    *,
    task_ids: set[str] | None = None,
    label: str | None = None,
) -> dict[str, Any]:
    suite_dir = Path(payload["suite"])
    rows: list[dict[str, Any]] = []
    skipped = 0
    for report in payload.get("reports") or []:
        task_id = report["task_id"]
        if task_ids is not None and task_id not in task_ids:
            continue
        summary = report.get("summary") or {}
        if not report.get("replay_ok") or summary.get("original_functional_gate") != 1.0:
            continue
        earliest = summary.get("earliest_pass_tokens")
        total = summary.get("total_tokens") or 0
        if earliest is None or not total:
            skipped += 1
            continue
        task_dir = suite_dir / task_id
        calls, actions = load_actions(task_dir)
        row = attribute_tail(calls=calls, actions=actions, cutoff=int(earliest), total=int(total))
        row["task_id"] = task_id
        row["kept_mutating"] = any(
            (item.get("tokens") or 0) > earliest for item in (report.get("unique") or [])
        )
        rows.append(row)
    out_label = label or suite_dir.name
    return {
        "suite": str(suite_dir),
        "mode": "earliest_pass",
        "skipped_no_gold": skipped,
        "summary": summarize_rows(rows, label=out_label),
        "tasks": [
            {
                "task_id": row["task_id"],
                "cutoff": row["cutoff"],
                "total": row["total"],
                "tail": row["tail"],
                "tail_frac": row["tail_frac"],
                "tok": row["tok"],
                "act": row["act"],
                "has_self_test": row["has_self_test"],
                "has_package_write": row["has_package_write"],
                "has_upstream_tests": row.get("has_upstream_tests"),
                "kept_mutating": row.get("kept_mutating"),
            }
            for row in rows
        ],
    }


def analyze_phase0_suite(
    payload: dict[str, Any],
    *,
    outcome: str = "pass",
    task_ids: set[str] | None = None,
    label: str | None = None,
) -> dict[str, Any]:
    suite_dir = Path(payload["suite"])
    rows: list[dict[str, Any]] = []
    for task in payload.get("tasks") or []:
        task_id = task["task_id"]
        if task_ids is not None and task_id not in task_ids:
            continue
        if outcome == "pass" and not task.get("functional_pass"):
            continue
        if outcome == "fail" and task.get("functional_pass"):
            continue
        last_write = task.get("last_write_tokens")
        total = task.get("total_tokens") or 0
        if last_write is None or not total:
            continue
        task_dir = suite_dir / task_id
        calls, actions = load_actions(task_dir)
        row = attribute_tail(calls=calls, actions=actions, cutoff=int(last_write), total=int(total))
        row["task_id"] = task_id
        rows.append(row)
    out_label = label or f"{suite_dir.name}:{outcome}:after_last_write"
    return {
        "suite": str(suite_dir),
        "mode": f"last_write_{outcome}",
        "summary": summarize_rows(rows, label=out_label),
        "tasks": [
            {
                "task_id": row["task_id"],
                "cutoff": row["cutoff"],
                "total": row["total"],
                "tail": row["tail"],
                "tail_frac": row["tail_frac"],
                "tok": row["tok"],
                "act": row["act"],
                "has_self_test": row["has_self_test"],
                "has_package_write": row["has_package_write"],
                "has_upstream_tests": row.get("has_upstream_tests"),
            }
            for row in rows
        ],
    }


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _print_summary(block: dict[str, Any]) -> None:
    summary = block["summary"]
    print(f"== {summary.get('label')}  n={summary.get('n')}  mode={block.get('mode')} ==")
    if not summary.get("n"):
        return
    print(
        f"  cutoff median={summary['cutoff_median']:.0f}  "
        f"total median={summary['total_median']:.0f}  "
        f"tail median={summary['tail_median']:.0f}  "
        f"tail_frac median={summary['tail_frac_median']:.3f}"
    )
    rates = summary["rates"]
    print(
        f"  has_self_test={rates['has_self_test']:.1%}  "
        f"has_package_write={rates['has_package_write']:.1%}  "
        f"has_upstream_tests={rates['has_upstream_tests']:.1%}  "
        f"tail_frac>=50%={rates['tail_frac_ge_50']:.1%}"
    )
    print(
        f"  pooled self_test={summary['pooled_self_test_share']:.1%}  "
        f"inspect={summary['pooled_inspect_share']:.1%}  "
        f"package_write={summary['pooled_package_write_share']:.1%}"
    )
    shares = sorted(summary.get("pooled_share") or {}, key=lambda k: -summary["pooled_share"][k])
    for key in shares[:8]:
        print(f"    {key:24} {summary['pooled_share'][key]:6.1%}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase1", type=Path, help="token_utility_phase1_*.json")
    parser.add_argument("--phase0", type=Path, help="token_utility_phase0_*.json")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--e50-ids", type=Path, help="JSON list of External-50 task ids")
    parser.add_argument("--label-filter", default="", help="Substring filter on suite path")
    parser.add_argument(
        "--phase0-outcome",
        default="pass",
        choices=("pass", "fail", "all"),
    )
    args = parser.parse_args()
    e50: set[str] | None = None
    if args.e50_ids:
        raw = json.loads(args.e50_ids.read_text(encoding="utf-8"))
        if isinstance(raw, dict) and "task_ids" in raw:
            e50 = set(raw["task_ids"])
        else:
            e50 = set(raw)
    blocks: list[dict[str, Any]] = []
    if args.phase1:
        phase1 = _load_json(args.phase1)
        for payload in phase1.get("reports") or []:
            suite = payload.get("suite") or ""
            if args.label_filter and args.label_filter not in suite:
                continue
            blocks.append(analyze_phase1_suite(payload, task_ids=None))
            if e50 is not None:
                blocks.append(
                    analyze_phase1_suite(
                        payload,
                        task_ids=e50,
                        label=f"{Path(suite).name}:e50",
                    )
                )
    if args.phase0:
        phase0 = _load_json(args.phase0)
        outcomes = (
            ("pass", "fail") if args.phase0_outcome == "all" else (args.phase0_outcome,)
        )
        for payload in phase0.get("reports") or phase0.get("suites") or []:
            if "suite" not in payload and "path" in payload:
                payload = {**payload, "suite": payload["path"]}
            suite = payload.get("suite") or payload.get("suite_dir") or ""
            if args.label_filter and args.label_filter not in str(suite):
                continue
            for outcome in outcomes:
                blocks.append(
                    analyze_phase0_suite(payload, outcome=outcome, task_ids=e50)
                )
    for block in blocks:
        _print_summary(block)
    slim = []
    for block in blocks:
        slim.append(
            {
                "suite": block["suite"],
                "mode": block["mode"],
                "summary": block["summary"],
                "n_tasks": len(block["tasks"]),
            }
        )
    _write_json(
        args.output,
        {"blocks": slim, "full": [{"suite": b["suite"], "mode": b["mode"], "summary": b["summary"], "tasks": b["tasks"]} for b in blocks]},
    )
    print("wrote", args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
