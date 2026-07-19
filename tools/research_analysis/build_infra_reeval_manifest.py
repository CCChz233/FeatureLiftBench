#!/usr/bin/env python3
"""Build the immutable re-evaluation manifest for historical infra failures."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RECORDS = REPO_ROOT / "artifacts/research_analysis/trajectory_records.csv"
DEFAULT_OUTPUT = REPO_ROOT / "artifacts/research_analysis/v1_1/infra_reeval_manifest.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", type=Path, default=DEFAULT_RECORDS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    with args.records.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    selected = [
        row for row in rows if int(row.get("evaluator_environment_error_count") or 0) > 0
    ]
    groups: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in selected:
        run_path = REPO_ROOT / str(row.get("run_path") or "")
        if run_path.name != "run.json":
            raise ValueError(f"unexpected run path: {run_path}")
        suite_dir = run_path.parent.parent
        submission = REPO_ROOT / str(row.get("submission_path") or "")
        groups[suite_dir.relative_to(REPO_ROOT).as_posix()].append(
            {
                "task_id": row["task_id"],
                "run_id": row["run_id"],
                "run_path": row["run_path"],
                "submission_path": row["submission_path"],
                "evaluation_path": row["evaluation_path"],
                "failure_flags": row["failure_flags"],
                "source_run_exists": run_path.is_file(),
                "source_submission_exists": submission.is_dir(),
            }
        )
    payload = {
        "schema_version": "featureliftbench.infra_reeval_manifest.v1",
        "source_records": args.records.relative_to(REPO_ROOT).as_posix(),
        "selection_rule": "evaluator_environment_error_count > 0",
        "run_count": len(selected),
        "unique_task_count": len({row["task_id"] for row in selected}),
        "suite_count": len(groups),
        "suites": [
            {
                "source_suite": suite,
                "output_suffix": Path(suite).name,
                "task_ids": sorted({item["task_id"] for item in values}),
                "runs": sorted(values, key=lambda item: (item["task_id"], item["run_id"])),
            }
            for suite, values in sorted(groups.items())
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"wrote {args.output}: runs={payload['run_count']} tasks={payload['unique_task_count']} "
        f"suites={payload['suite_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
