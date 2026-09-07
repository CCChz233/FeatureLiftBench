#!/usr/bin/env python3
"""Sample the Obligation-Guided 30-task screening slice. Does not run agents."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "harness"))

from featureliftbench.obligation_guided.sample import SEED
from featureliftbench.obligation_guided.sample import artifact_failure_rows_from_suite
from featureliftbench.obligation_guided.sample import attach_stages_from_suites
from featureliftbench.obligation_guided.sample import load_annotation_rows
from featureliftbench.obligation_guided.sample import python150_task_ids
from featureliftbench.obligation_guided.sample import sample_pilot30
from featureliftbench.obligation_guided.sample import write_task_list

DEFAULT_ANNOTATIONS = (
    _REPO_ROOT
    / "reports/paper_analysis/python150_prime_v2_analysis_20260905"
    / "failure_root_cause_annotations.csv"
)
DEFAULT_PRO_SUITE = (
    _REPO_ROOT
    / "experiments/python/openhands/deepseek-v4-pro/python150-prime-v2-main-r1"
)
DEFAULT_FLASH_SUITE = (
    _REPO_ROOT
    / "experiments/python/openhands/deepseek-v4-flash/python200-prime-v2-main-r1"
)
DEFAULT_TASKS = _REPO_ROOT / "benchmark" / "tasks"
DEFAULT_LIST = (
    _REPO_ROOT / "harness/config/experiments/obligation_guided_pilot30_v1.txt"
)
DEFAULT_MANIFEST = (
    _REPO_ROOT / "harness/config/experiments/obligation_guided_pilot30_v1.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations", type=Path, default=DEFAULT_ANNOTATIONS)
    parser.add_argument("--pro-suite", type=Path, default=DEFAULT_PRO_SUITE)
    parser.add_argument("--flash-suite", type=Path, default=DEFAULT_FLASH_SUITE)
    parser.add_argument("--tasks-root", type=Path, default=DEFAULT_TASKS)
    parser.add_argument("--seed", default=SEED)
    parser.add_argument(
        "--model",
        default="flash",
        help="Restrict the pool to this backend (default flash). Use 'all' for Pro+Flash unique tasks.",
    )
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--list-path", type=Path, default=DEFAULT_LIST)
    parser.add_argument("--manifest-path", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()

    allowed = python150_task_ids(args.tasks_root) if args.tasks_root.is_dir() else None
    rows = []
    sources = []
    if args.annotations.is_file():
        loaded = load_annotation_rows(args.annotations)
        if allowed is not None:
            loaded = [row for row in loaded if row.get("task_id") in allowed]
        loaded = attach_stages_from_suites(
            loaded,
            flash_suite=args.flash_suite,
            pro_suite=args.pro_suite,
        )
        rows.extend(loaded)
        sources.append(str(args.annotations))
    else:
        for suite_dir, model in (
            (args.flash_suite, "deepseek/deepseek-v4-flash"),
            (args.pro_suite, "deepseek/deepseek-v4-pro"),
        ):
            suite_rows = artifact_failure_rows_from_suite(
                suite_dir=suite_dir,
                model=model,
                allowed_task_ids=allowed,
            )
            if suite_rows:
                rows.extend(suite_rows)
                sources.append(str(suite_dir))
    if not rows:
        print(
            "no annotation CSV or suite.json artifact failures found; "
            "refusing to invent a 30-task list",
            file=sys.stderr,
        )
        return 2
    try:
        payload = sample_pilot30(
            rows,
            seed=args.seed,
            model=None if args.model.strip().lower() in {"", "all"} else args.model,
        )
    except ValueError as exc:
        print(f"sampling failed: {exc}", file=sys.stderr)
        return 1
    payload["sources"] = sources
    print(json.dumps(payload, indent=2, sort_keys=True))
    if args.write:
        write_task_list(args.list_path, payload["task_ids"])
        args.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        args.manifest_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"wrote {args.list_path}", file=sys.stderr)
        print(f"wrote {args.manifest_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
