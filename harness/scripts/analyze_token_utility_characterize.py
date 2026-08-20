#!/usr/bin/env python3
"""Stratify T*/T_total, post-sufficiency tokens, and verification share.

Offline characterization. Gold is Phase 1 earliest sufficient snapshot.
Stratifies by model, lift type (Direct/Adapted/Composite), and construction
cohort (python150 / hard3 / external50). Does not treat metadata.difficulty
as a scientific easy/medium/hard label. Does not write a stopping rule.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "harness"))

from featureliftbench.token_utility_axes import (  # noqa: E402
    load_lift_types,
    load_task_axes,
    model_label,
)
from featureliftbench.token_utility_signals import iter_gold_pass_reports  # noqa: E402

SELF_TEST_KEYS = ("self_test_run", "self_test_write")


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


def load_post_pass_index(paths: Iterable[Path]) -> dict[tuple[str, str], dict[str, Any]]:
    index: dict[tuple[str, str], dict[str, Any]] = {}
    for path in paths:
        if not path.is_file():
            continue
        payload = _load_json(path)
        for block in payload.get("full") or []:
            suite = str(block.get("suite") or "")
            for task in block.get("tasks") or []:
                task_id = task.get("task_id")
                if suite and task_id:
                    index[(suite, str(task_id))] = task
    return index


def gold_row(
    suite: str,
    report: dict[str, Any],
    summary: dict[str, Any],
    *,
    axes: dict[str, Any],
    post: dict[str, Any] | None,
) -> dict[str, Any]:
    t_star = int(summary["earliest_pass_tokens"])
    total = int(summary.get("total_tokens") or report.get("total_tokens") or 0)
    tail = max(0, total - t_star) if total else None
    frac = (t_star / total) if total else None
    tok = (post or {}).get("tok") or {}
    tail_billed = int((post or {}).get("tail") or 0)
    self_test = sum(int(tok.get(key) or 0) for key in SELF_TEST_KEYS)
    return {
        "suite": suite,
        "model": model_label(suite),
        "task_id": report["task_id"],
        "lift_type": axes.get("lift_type"),
        "cohort": axes.get("cohort"),
        "entanglement_level": axes.get("entanglement_level"),
        "t_star": t_star,
        "total_tokens": total,
        "tstar_frac": frac,
        "tail_tokens": tail,
        "tail_frac": (tail / total) if total and tail is not None else None,
        "late_pass": bool(t_star >= 2_000_000),
        "verification_tokens": self_test if post else None,
        "verification_share": (self_test / tail_billed) if post and tail_billed else None,
    }


def summarize(rows: list[dict[str, Any]], *, label: str) -> dict[str, Any]:
    if not rows:
        return {"label": label, "n": 0}
    fracs = [row["tstar_frac"] for row in rows if row.get("tstar_frac") is not None]
    tails = [float(row["tail_tokens"]) for row in rows if row.get("tail_tokens") is not None]
    tail_fracs = [row["tail_frac"] for row in rows if row.get("tail_frac") is not None]
    totals = [float(row["total_tokens"]) for row in rows if row.get("total_tokens")]
    tstars = [float(row["t_star"]) for row in rows if row.get("t_star") is not None]
    verif = [row["verification_share"] for row in rows if row.get("verification_share") is not None]
    return {
        "label": label,
        "n": len(rows),
        "tstar_frac_median": _quantile(fracs, 0.5),
        "tstar_frac_p25": _quantile(fracs, 0.25),
        "tstar_frac_p75": _quantile(fracs, 0.75),
        "t_star_median": _quantile(tstars, 0.5),
        "total_median": _quantile(totals, 0.5),
        "tail_median": _quantile(tails, 0.5),
        "tail_frac_median": _quantile(tail_fracs, 0.5),
        "verification_share_median": _quantile(verif, 0.5),
        "late_pass_n": sum(1 for row in rows if row.get("late_pass")),
        "small_n": len(rows) < 8,
    }


def group_rows(rows: list[dict[str, Any]], keys: tuple[str, ...]) -> list[dict[str, Any]]:
    buckets: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        buckets[tuple(row.get(key) for key in keys)].append(row)
    out = []
    for key, group in sorted(buckets.items(), key=lambda item: [str(part) for part in item[0]]):
        label = "|".join(str(part) for part in key)
        summary = summarize(group, label=label)
        for name, value in zip(keys, key):
            summary[name] = value
        out.append(summary)
    return out


def collect_rows(
    phase1_paths: list[Path],
    *,
    post_index: dict[tuple[str, str], dict[str, Any]],
    tasks_root: Path,
) -> list[dict[str, Any]]:
    lifts = load_lift_types()
    seen: set[tuple[str, str]] = set()
    rows: list[dict[str, Any]] = []
    for path in phase1_paths:
        phase1 = _load_json(path)
        for suite, report, summary in iter_gold_pass_reports(phase1):
            key = (suite, report["task_id"])
            if key in seen:
                continue
            seen.add(key)
            axes = load_task_axes(report["task_id"], tasks_root=tasks_root, lift_types=lifts)
            rows.append(
                gold_row(
                    suite,
                    report,
                    summary,
                    axes=axes,
                    post=post_index.get(key),
                )
            )
    return rows


def _print_table(title: str, summaries: list[dict[str, Any]]) -> None:
    print(f"== {title} ==")
    print(
        f"{'slice':40} {'n':>4} {'T*/T':>6} {'T*':>8} {'tail':>8} "
        f"{'tail%':>6} {'verif':>6} {'late':>4}"
    )
    for row in summaries:
        if not row.get("n"):
            continue
        tstar = (row.get("t_star_median") or 0) / 1e6
        tail = (row.get("tail_median") or 0) / 1e6
        verif = row.get("verification_share_median")
        flag = " *" if row.get("small_n") else ""
        print(
            f"{row['label'][:40]:40} {row['n']:4d} "
            f"{(row.get('tstar_frac_median') or 0):6.2f} "
            f"{tstar:7.2f}M {tail:7.2f}M "
            f"{(row.get('tail_frac_median') or 0):6.0%} "
            f"{(verif if verif is not None else float('nan')):6.0%} "
            f"{row.get('late_pass_n'):4d}{flag}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase1", type=Path, nargs="+", required=True)
    parser.add_argument("--post-pass", type=Path, nargs="*", default=[])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--tasks-root",
        type=Path,
        default=_REPO_ROOT / "benchmark/python200_tasks",
    )
    args = parser.parse_args()
    post_index = load_post_pass_index(args.post_pass)
    rows = collect_rows(args.phase1, post_index=post_index, tasks_root=args.tasks_root)
    flash200 = [row for row in rows if row["model"] == "flash_local_main200"]
    e50 = [row for row in rows if row["model"].endswith("_e50")]
    tables = {
        "by_model": group_rows(rows, ("model",)),
        "flash200_by_lift": group_rows(flash200, ("lift_type",)),
        "flash200_by_cohort": group_rows(flash200, ("cohort",)),
        "flash200_by_entanglement_level": group_rows(flash200, ("entanglement_level",)),
        "flash200_lift_x_cohort": group_rows(flash200, ("lift_type", "cohort")),
        "e50_by_model": group_rows(e50, ("model",)),
        "e50_by_lift": group_rows(e50, ("lift_type",)),
        "e50_model_x_lift": group_rows(e50, ("model", "lift_type")),
        "all_model_x_lift": group_rows(rows, ("model", "lift_type")),
    }
    _print_table("model", tables["by_model"])
    _print_table("Flash Main-200 × lift", tables["flash200_by_lift"])
    _print_table("Flash Main-200 × cohort (informal difficulty)", tables["flash200_by_cohort"])
    _print_table("Flash Main-200 × lift × cohort", tables["flash200_lift_x_cohort"])
    _print_table("E50 × model", tables["e50_by_model"])
    _print_table("E50 × model × lift", tables["e50_model_x_lift"])
    payload = {
        "gold": "earliest sufficient snapshot T*",
        "not_a_stopping_rule": True,
        "difficulty_note": (
            "cohort is construction history (python150 / hard3 / external50). "
            "metadata.difficulty is 150=hard and E50=medium by construction and "
            "must not be reported as scientific easy/medium/hard."
        ),
        "n_rows": len(rows),
        "tables": tables,
        "tasks": rows,
    }
    _write_json(args.output, payload)
    print("wrote", args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
