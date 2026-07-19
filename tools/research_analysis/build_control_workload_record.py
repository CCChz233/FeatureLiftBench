#!/usr/bin/env python3
"""Record auditable control-preflight workload evidence without inventing person-hours."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUN_ROOT = ROOT / "experiments/v1_1_control_preflight"
OUTPUT = ROOT / "artifacts/research_analysis/v1_1/control_workload_record.json"
LOG = ROOT / "artifacts/research_analysis/v1_1/control_workload_prospective_log.csv"
TASKS = ("boltons__iterutils_core__001", "pluggy__hook_specs_core__001")
VARIANTS = ("alternative_v11", "copy_heavy_v11", "narrow_v11")
PILOT_10 = (
    "pluggy__hook_specs_core__001", "pydantic_v1__validation_error_core__001",
    "coverage__config_merge_core__001", "lark__grammar_loader_core__001",
    "websockets__handshake_parse_core__001", "boltons__iterutils_core__001",
    "schema__nested_validate_core__hard3_001", "requests_cache__cache_key_core__hard3_001",
    "sqlparse__format_filters_core__001", "celery__signal_dispatch_core__hard3_001",
)


def iso(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()


def main() -> int:
    results = sorted(RUN_ROOT.glob("*/*/rep-*/result.json"))
    mtimes = [path.stat().st_mtime for path in results]
    variant_records = []
    for task_id in TASKS:
        for variant in VARIANTS:
            matching = sorted(RUN_ROOT.glob(f"{task_id}/{variant}/rep-*/result.json"))
            variant_records.append(
                {
                    "task_id": task_id,
                    "variant": variant,
                    "evaluator_run_count": len(matching),
                    "result_paths": [str(path.relative_to(ROOT)) for path in matching],
                    "non_environment_rework_rounds": None,
                    "authoring_person_hours": None,
                }
            )
    payload = {
        "schema_version": "featureliftbench.control_workload_record.v1",
        "instrumentation": {
            "retrospective_human_timer_available": False,
            "observed_person_hours": None,
            "observed_non_environment_rework_rounds": None,
            "evaluator_run_count": len(results),
            "first_result_utc": iso(min(mtimes)) if mtimes else None,
            "last_result_utc": iso(max(mtimes)) if mtimes else None,
            "limitation": (
                "File timestamps bound evaluator activity only. They are not authoring time and are never "
                "converted into person-hours."
            ),
        },
        "formal_workload_gate": {
            "status": "unverified_missing_prospective_human_log",
            "maximum_total_person_hours": 16,
            "maximum_non_environment_rework_rounds_per_submission": 2,
        },
        "engineering_scope_decision": {
            "status": "proceed_staged_with_prospective_logging",
            "completed_task_ids": list(TASKS),
            "remaining_task_ids": [task_id for task_id in PILOT_10 if task_id not in TASKS],
            "mandatory_variants": list(VARIANTS),
            "batch_size": 2,
            "stop_conditions": [
                "any submission exceeds two non-environment repair rounds",
                "prospective total projects above ten person-days",
                "alternative cannot pass three isolated Oracle-equivalent evaluations",
            ],
            "paper_claim_boundary": (
                "The two-task functional feasibility result is usable; no labor-cost claim is allowed until "
                "the prospective log is complete."
            ),
        },
        "variant_records": variant_records,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not LOG.exists():
        with LOG.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "task_id", "variant", "authoring_started_utc", "authoring_finished_utc",
                    "person_hours", "non_environment_rework_rounds", "evaluator_runs",
                    "reviewer", "notes",
                ],
            )
            writer.writeheader()
            for task_id in payload["engineering_scope_decision"]["remaining_task_ids"]:
                for variant in VARIANTS:
                    writer.writerow({"task_id": task_id, "variant": variant})
    print(f"wrote {OUTPUT.relative_to(ROOT)} and {LOG.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
