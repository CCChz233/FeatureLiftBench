#!/usr/bin/env python3
"""Aggregate the two-task v1.1 control preflight into an auditable report."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "harness"))

from featureliftbench.compactness import analyze_submission_footprint


RUN_ROOT = ROOT / "experiments/v1_1_control_preflight"
OUTPUT = ROOT / "artifacts/research_analysis/v1_1/control_preflight_results.json"
WORKLOAD_RECORD = ROOT / "artifacts/research_analysis/v1_1/control_workload_record.json"


def _passed(result: dict, phase: str) -> bool:
    value = result.get(phase)
    return bool(value.get("passed")) if isinstance(value, dict) else False


def main() -> int:
    records: list[dict] = []
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for result_path in sorted(RUN_ROOT.glob("*/*/rep-*/result.json")):
        task_id, variant, repeat = result_path.parts[-4:-1]
        result = json.loads(result_path.read_text(encoding="utf-8"))
        functional = _passed(result, "public_tests") and _passed(result, "hidden_tests")
        submission = ROOT / "benchmark/submissions" / task_id / variant
        footprint = analyze_submission_footprint(
            ROOT / "benchmark/tasks" / task_id,
            submission,
            functional_pass=functional,
        )
        record = {
            "task_id": task_id,
            "variant": variant,
            "repeat": repeat,
            "status": result.get("status"),
            "build_pass": bool(result.get("build_pass")),
            "public_pass": _passed(result, "public_tests"),
            "hidden_pass": _passed(result, "hidden_tests"),
            "functional_pass": functional,
            "result_path": str(result_path.relative_to(ROOT)),
            "submission_path": str(submission.relative_to(ROOT)),
            **footprint,
        }
        records.append(record)
        grouped[(task_id, variant)].append(record)

    checks: list[dict] = []
    for task_id in sorted({record["task_id"] for record in records}):
        by_variant = {
            variant: grouped[(task_id, variant)]
            for variant in ("alternative_v11", "copy_heavy_v11", "narrow_v11")
        }
        alt = by_variant["alternative_v11"]
        copy = by_variant["copy_heavy_v11"]
        narrow = by_variant["narrow_v11"]
        checks.append({
            "task_id": task_id,
            "alternative_three_stable_passes": len(alt) == 3 and all(r["functional_pass"] for r in alt),
            "copy_heavy_functional_pass": bool(copy) and all(r["functional_pass"] for r in copy),
            "copy_heavy_detected": bool(copy) and all(r["compactness_class"] == "copy_heavy_pass" for r in copy),
            "narrow_public_runnable": bool(narrow) and all(r["public_pass"] for r in narrow),
            "narrow_rejected_by_hidden": bool(narrow) and all(not r["hidden_pass"] for r in narrow),
        })

    automated_gate = all(all(value for key, value in row.items() if key != "task_id") for row in checks)
    workload = json.loads(WORKLOAD_RECORD.read_text(encoding="utf-8")) if WORKLOAD_RECORD.is_file() else {}
    payload = {
        "schema_version": "featureliftbench.control_preflight.v1",
        "tasks": sorted({record["task_id"] for record in records}),
        "records": records,
        "acceptance_checks": checks,
        "automated_functional_gate_passed": automated_gate,
        "workload_gate": {
            "status": (workload.get("formal_workload_gate") or {}).get("status", "needs_human_time_log"),
            "maximum_total_person_hours": 16,
            "maximum_non_environment_rework_rounds_per_submission": 2,
            "observed_person_hours": None,
            "observed_rework_rounds": None,
            "pilot10_projection_person_days": None,
            "note": "Wall-clock and human authoring time were not instrumented; do not infer them from evaluator runs.",
        },
        "engineering_scope_decision": workload.get("engineering_scope_decision") or {},
        "interpretation_boundary": (
            "The automated functionality/discrimination gate is auditable. The workload gate remains unverified "
            "until authors supply time and rework logs."
        ),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)} with {len(records)} run records")
    print(f"automated_functional_gate_passed={automated_gate}")
    return 0 if automated_gate else 1


if __name__ == "__main__":
    raise SystemExit(main())
