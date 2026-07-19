#!/usr/bin/env python3
"""Validate v1.1 release gates without treating review scaffolds as completed gold."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "harness"))

from featureliftbench.freeze import file_manifest, manifest_digest  # noqa: E402


STATUS = ROOT / "artifacts/research_analysis/v1_1/v1_1_audit_status.json"
QUEUE = ROOT / "artifacts/research_analysis/v1_1/review_queue.csv"
NEAR_DUPLICATES = ROOT / "artifacts/research_analysis/v1_1/near_duplicate_review_queue.csv"
ANNOTATION_INTEGRITY = ROOT / "artifacts/research_analysis/v1_1/annotation_integrity_report.json"
OUTPUT = ROOT / "artifacts/research_analysis/v1_1/release_gate_report.json"
CURRENT_FREEZE_POINTER = ROOT / "artifacts/research_analysis/v1_1/current_oracle_freeze.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def check(name: str, satisfied: bool, evidence: Any, blocker: str) -> dict[str, Any]:
    return {"gate": name, "satisfied": satisfied, "evidence": evidence, "blocker": "" if satisfied else blocker}


def main() -> int:
    status = load(STATUS)
    with QUEUE.open(encoding="utf-8", newline="") as handle:
        queue = list(csv.DictReader(handle))
    with NEAR_DUPLICATES.open(encoding="utf-8", newline="") as handle:
        duplicate_queue = list(csv.DictReader(handle))
    annotation_integrity = load(ANNOTATION_INTEGRITY)
    week1 = status["week1_execution"]
    behavior = status["behavior_contracts"]
    closure = status["diagnostic_closure_gold"]
    taxonomy = status["taxonomy"]
    taxonomy_ai_count = int(taxonomy["review_status_counts"].get("ai_assisted_reviewed_v1", 0))
    behavior_human_count = sum(
        int(behavior["status_counts"].get(value, 0))
        for value in ("author_reviewed", "double_reviewed", "adjudicated")
    )
    closure_human_count = sum(
        int(closure["review_status_counts"].get(value, 0))
        for value in ("double_reviewed", "adjudicated")
    )
    gates = [
        check("oracle_canary", week1["oracle_canary_gate_pass"] is True, week1["oracle_canary_run_count"], "15/15 canary required"),
        check("oracle_full_results", week1["oracle_full_run_count"] == 450 and week1["oracle_unstable_task_count"] == 0 and week1["oracle_incomplete_task_count"] == 0, week1, "450 complete stable results required"),
        check("quarantine_explained", week1["oracle_stable_pass_task_count"] + week1["oracle_quarantined_task_count"] == 150, week1["oracle_quarantined_task_count"], "every nonpassing task must be versioned and explained"),
        check("historical_infra_reevaluation", week1["historical_infra_reevaluation_gate_pass"] is True, week1["historical_infra_new_result_count"], "62 complete re-evaluations with zero new infra failures required"),
        check("historical_outputs_immutable", week1["historical_output_hash_mismatch_count"] == 0, week1["historical_output_hash_mismatch_count"], "historical hash mismatch"),
        check("behavior_contract_review", behavior_human_count == 150 and behavior["public_unmapped_count"] == 0 and behavior["hidden_unmapped_count"] == 0, behavior, "behavior mappings require independent human review/adjudication"),
        check("annotation_integrity", annotation_integrity.get("integrity_gate_pass") is True, annotation_integrity, "annotation paths/nodeids/hashes/reviewer structure invalid"),
        check("diagnostic40_closure_gold", closure_human_count == 40 and closure["file_completeness_counts"].get("complete", 0) == 40, closure, "40 complete independently reviewed/adjudicated file closures required"),
        check("taxonomy_adjudication", taxonomy["needs_review_count"] == 0 and taxonomy_ai_count == 0, taxonomy, "AI-assisted taxonomy rows require human adjudication"),
        check(
            "near_duplicate_semantic_review",
            all(row.get("review_status") == "adjudicated" for row in duplicate_queue),
            {"candidate_clusters": len(duplicate_queue), "needs_review": sum(row.get("review_status") != "adjudicated" for row in duplicate_queue)},
            "eight candidate clusters require human semantic review",
        ),
        check("representative20_active", not week1["representative20_quarantined_task_ids"], week1["representative20_quarantined_task_ids"], "repair/adjudicate fixed Representative-20 tasks"),
        check("control_functional_preflight", status["control_preflight"]["automated_functional_gate_passed"] is True, status["control_preflight"], "control functionality gate failed"),
        check("control_workload_preflight", status["control_preflight"]["workload_gate_status"] == "passed", status["control_preflight"]["workload_gate_status"], "human time/rework log required"),
    ]
    paper_release_ready = all(item["satisfied"] for item in gates)
    engineering_pilot_ready = bool(status.get("readiness", {}).get("engineering_pilot_ready"))
    pointer = load(CURRENT_FREEZE_POINTER) if CURRENT_FREEZE_POINTER.is_file() else {}
    freeze_id = str(pointer.get("freeze_id") or "")
    oracle_root = ROOT / "experiments/v1_1_oracle_validation" / freeze_id
    release_inputs = (
        ROOT / "benchmark/tasks",
        ROOT / "artifacts/research_analysis/python150_task_taxonomy.csv",
        STATUS,
        QUEUE,
        NEAR_DUPLICATES,
        ANNOTATION_INTEGRITY,
        ROOT / "artifacts/research_analysis/v1_1/control_preflight_results.json",
        ROOT / "artifacts/research_analysis/v1_1/behavior_review_audit.json",
        ROOT / "artifacts/research_analysis/v1_1/diagnostic_closure_review_audit.json",
        oracle_root / "canary/summary.json",
        oracle_root / "full/summary.json",
        oracle_root / "quarantine_manifest.json",
        ROOT / "experiments/v1_1_infra_reevaluation/536c2beec549fdc8/analysis.json",
    )
    payload = {
        "schema_version": "featureliftbench.v1_1_release_gate_report.v1",
        "release_ready": paper_release_ready,
        "paper_release_ready": paper_release_ready,
        "pilot_freeze_ready": engineering_pilot_ready,
        "engineering_pilot_ready": engineering_pilot_ready,
        "pilot_evidence_status": "provisional_ai_assisted_annotations" if engineering_pilot_ready else "blocked",
        "gate_count": len(gates),
        "passed_gate_count": sum(item["satisfied"] for item in gates),
        "gates": gates,
        "open_review_rows": sum(row["required_actions"] != "" for row in queue),
    }
    payload["release_input_files"] = file_manifest(release_inputs, root=ROOT)
    payload["release_inputs_sha256"] = manifest_digest({"files": payload["release_input_files"]})
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("release_ready", "pilot_freeze_ready", "gate_count", "passed_gate_count", "open_review_rows")}, indent=2))
    return 0 if payload["release_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
