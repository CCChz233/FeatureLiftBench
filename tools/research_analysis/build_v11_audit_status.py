#!/usr/bin/env python3
"""Build the v1.1 annotation/freeze readiness report from repository assets."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TASKS = ROOT / "benchmark/tasks"
SUBSET = ROOT / "artifacts/research_analysis/v1_1/diagnostic_subset_manifest.json"
TAXONOMY = ROOT / "artifacts/research_analysis/python150_task_taxonomy.csv"
OUTPUT_JSON = ROOT / "artifacts/research_analysis/v1_1/v1_1_audit_status.json"
OUTPUT_MD = ROOT / "docs/reference/research_analysis/V11_IMPLEMENTATION_STATUS.md"
CURRENT_FREEZE_POINTER = ROOT / "artifacts/research_analysis/v1_1/current_oracle_freeze.json"
INFRA_ANALYSIS = ROOT / "experiments/validation/v1_1/v1_1_infra_reevaluation/536c2beec549fdc8/analysis.json"
CONTROL_RESULTS = ROOT / "artifacts/research_analysis/v1_1/control_preflight_results.json"
NEAR_DUPLICATE_QUEUE = ROOT / "artifacts/research_analysis/v1_1/near_duplicate_review_queue.csv"
BEHAVIOR_REVIEW = ROOT / "artifacts/research_analysis/v1_1/behavior_review_audit.json"
CLOSURE_REVIEW = ROOT / "artifacts/research_analysis/v1_1/diagnostic_closure_review_audit.json"
RELEASE_GATE = ROOT / "artifacts/research_analysis/v1_1/release_gate_report.json"
PILOT_FREEZE = ROOT / "experiments/methods/ecsm_pilot/pilot_freeze_manifest.json"
PILOT_AUTHORIZATION = ROOT / "artifacts/research_analysis/v1_1/pilot_execution_authorization_status.json"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def main() -> int:
    task_dirs = sorted(path for path in TASKS.iterdir() if (path / "metadata.json").is_file())
    subset = load_json(SUBSET)
    diagnostic = set(subset["representative_20"]) | set(subset["challenge_20"])
    contract_status = Counter()
    public_total = hidden_total = public_unmapped = hidden_unmapped = 0
    contract_review_queue: list[str] = []
    missing_task_docs: list[str] = []
    hard_role_count = 0
    for task_dir in task_dirs:
        if not (task_dir / "TASK.md").is_file():
            missing_task_docs.append(task_dir.name)
        metadata = load_json(task_dir / "metadata.json")
        if metadata.get("split_role") == "mechanism_challenging":
            hard_role_count += 1
        contract_path = task_dir / "evaluation/behavior_contract.json"
        if not contract_path.is_file():
            contract_status["missing"] += 1
            contract_review_queue.append(task_dir.name)
            continue
        contract = load_json(contract_path)
        status = str(contract.get("review_status") or "unknown")
        contract_status[status] += 1
        public = contract.get("public_test_mappings") or []
        hidden = contract.get("hidden_test_mappings") or []
        public_total += len(public)
        hidden_total += len(hidden)
        public_unmapped += sum(not row.get("public_clause_ids") for row in public if isinstance(row, dict))
        hidden_unmapped += sum(not row.get("public_clause_ids") for row in hidden if isinstance(row, dict))
        if status not in {"author_reviewed", "double_reviewed", "adjudicated"}:
            contract_review_queue.append(task_dir.name)

    closure_status = Counter()
    file_completeness = Counter()
    closure_review_queue: list[str] = []
    for task_id in sorted(diagnostic):
        path = TASKS / task_id / "evaluation/closure_gold.json"
        if not path.is_file():
            closure_status["missing"] += 1
            file_completeness["missing"] += 1
            closure_review_queue.append(task_id)
            continue
        closure = load_json(path)
        status = str((closure.get("review") or {}).get("status") or "unknown")
        complete = str((closure.get("gold_completeness") or {}).get("file") or "unresolved")
        closure_status[status] += 1
        file_completeness[complete] += 1
        if status != "adjudicated" or complete != "complete":
            closure_review_queue.append(task_id)

    taxonomy_review = Counter()
    taxonomy_queue: list[str] = []
    taxonomy_human_adjudication_queue: list[str] = []
    with TAXONOMY.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            status = row.get("review_status") or "unknown"
            taxonomy_review[status] += 1
            if status == "needs_review":
                taxonomy_queue.append(row["task_id"])
            if status in {"needs_review", "ai_assisted_reviewed_v1", "auto_assigned"}:
                taxonomy_human_adjudication_queue.append(row["task_id"])

    pointer = load_json(CURRENT_FREEZE_POINTER) if CURRENT_FREEZE_POINTER.is_file() else {}
    freeze_id = str(pointer.get("freeze_id") or "")
    oracle_root = ROOT / "experiments/validation/v1_1/v1_1_oracle_validation" / freeze_id
    canary = load_json(oracle_root / "canary/summary.json") if (oracle_root / "canary/summary.json").is_file() else {}
    full = load_json(oracle_root / "full/summary.json") if (oracle_root / "full/summary.json").is_file() else {}
    quarantine = load_json(oracle_root / "quarantine_manifest.json") if (oracle_root / "quarantine_manifest.json").is_file() else {"tasks": []}
    original_root = ROOT / "experiments/validation/v1_1/v1_1_oracle_validation/536c2beec549fdc8"
    history_after = load_json(original_root / "historical_outputs_after_verification.json") if (original_root / "historical_outputs_after_verification.json").is_file() else {}
    infra = load_json(INFRA_ANALYSIS) if INFRA_ANALYSIS.is_file() else {}
    controls = load_json(CONTROL_RESULTS) if CONTROL_RESULTS.is_file() else {}
    behavior_review = load_json(BEHAVIOR_REVIEW) if BEHAVIOR_REVIEW.is_file() else {}
    closure_review = load_json(CLOSURE_REVIEW) if CLOSURE_REVIEW.is_file() else {}
    release_gate = load_json(RELEASE_GATE) if RELEASE_GATE.is_file() else {}
    pilot_freeze = load_json(PILOT_FREEZE) if PILOT_FREEZE.is_file() else {}
    pilot_authorization = load_json(PILOT_AUTHORIZATION) if PILOT_AUTHORIZATION.is_file() else {}
    with NEAR_DUPLICATE_QUEUE.open(encoding="utf-8", newline="") as handle:
        duplicate_rows = list(csv.DictReader(handle))
    quarantined_ids = {str(item.get("task_id")) for item in quarantine.get("tasks") or []}
    representative_quarantined = sorted(quarantined_ids & set(subset["representative_20"]))
    challenge_quarantined = sorted(quarantined_ids & set(subset["challenge_20"]))
    priority_ids = set(subset["challenge_groups"]["pilot_10"]) | set(subset["challenge_groups"]["contract_review_6"])
    priority_review_rows = [row for row in behavior_review.get("tasks") or [] if row.get("task_id") in priority_ids]
    priority_behavior_clean = len(priority_review_rows) == 16 and all(
        int(row.get("conflict_count", 0)) == 0 and int(row.get("api_fallback_count", 0)) == 0
        for row in priority_review_rows
    )
    engineering_pilot_ready = bool(
        canary.get("gate_pass") is True
        and full.get("run_count") == 450
        and not full.get("unstable_task_ids")
        and not full.get("incomplete_task_ids")
        and not full.get("invalid_artifact_task_ids")
        and not representative_quarantined
        and not challenge_quarantined
        and public_unmapped == 0
        and hidden_unmapped == 0
        and priority_behavior_clean
        and closure_review.get("complete_file_task_count") == 40
        and not taxonomy_queue
        and all(row.get("review_status") == "ai_assisted_adjudicated" for row in duplicate_rows)
        and controls.get("automated_functional_gate_passed") is True
        and (controls.get("engineering_scope_decision") or {}).get("status") == "proceed_staged_with_prospective_logging"
    )

    payload = {
        "schema_version": "featureliftbench.v1_1_audit_status.v1",
        "task_count": len(task_dirs),
        "task_docs": {"present": len(task_dirs) - len(missing_task_docs), "missing_task_ids": missing_task_docs},
        "behavior_contracts": {
            "status_counts": dict(sorted(contract_status.items())),
            "public_test_mapping_count": public_total,
            "public_unmapped_count": public_unmapped,
            "hidden_test_mapping_count": hidden_total,
            "hidden_unmapped_count": hidden_unmapped,
            "human_review_queue_count": len(contract_review_queue),
            "human_review_queue_task_ids": sorted(contract_review_queue),
        },
        "diagnostic_closure_gold": {
            "task_count": len(diagnostic),
            "review_status_counts": dict(sorted(closure_status.items())),
            "file_completeness_counts": dict(sorted(file_completeness.items())),
            "human_review_queue_count": len(closure_review_queue),
            "human_review_queue_task_ids": closure_review_queue,
        },
        "taxonomy": {
            "review_status_counts": dict(sorted(taxonomy_review.items())),
            "needs_review_count": len(taxonomy_queue),
            "needs_review_task_ids": sorted(taxonomy_queue),
            "human_adjudication_queue_count": len(taxonomy_human_adjudication_queue),
            "human_adjudication_queue_task_ids": sorted(taxonomy_human_adjudication_queue),
        },
        "hard50_compatibility": {
            "physical_identifiers_renamed": False,
            "split_role_mechanism_challenging_count": hard_role_count,
        },
        "week1_execution": {
            "current_freeze_id": freeze_id,
            "oracle_canary_gate_pass": canary.get("gate_pass"),
            "oracle_canary_run_count": canary.get("run_count", 0),
            "oracle_full_run_count": full.get("run_count", 0),
            "oracle_stable_pass_task_count": int(full.get("task_count", 0)) - len(full.get("failed_task_ids") or []),
            "oracle_quarantined_task_count": len(quarantine.get("tasks") or []),
            "oracle_unstable_task_count": len(full.get("unstable_task_ids") or []),
            "oracle_incomplete_task_count": len(full.get("incomplete_task_ids") or []),
            "historical_output_hash_mismatch_count": history_after.get("mismatch_count"),
            "historical_infra_reevaluation_gate_pass": infra.get("gate_pass"),
            "historical_infra_new_result_count": infra.get("new_result_count", 0),
            "historical_infra_new_failure_count": infra.get("new_infrastructure_failure_count"),
            "representative20_quarantined_task_ids": representative_quarantined,
            "challenge20_quarantined_task_ids": challenge_quarantined,
        },
        "control_preflight": {
            "automated_functional_gate_passed": controls.get("automated_functional_gate_passed"),
            "workload_gate_status": (controls.get("workload_gate") or {}).get("status"),
        },
        "near_duplicate_review": {
            "candidate_cluster_count": len(duplicate_rows),
            "needs_review_count": sum(row.get("review_status") != "adjudicated" for row in duplicate_rows),
        },
        "readiness": {
            "automated_scaffolding_complete": (
                len(task_dirs) == 150 and not missing_task_docs and sum(contract_status.values()) == 150
            ),
            "behavior_contract_human_review_complete": (
                not contract_review_queue and not public_unmapped and not hidden_unmapped
            ),
            "diagnostic40_closure_double_review_complete": not closure_review_queue,
            "taxonomy_adjudication_complete": not taxonomy_human_adjudication_queue,
            "oracle_canary_allowed_after_evaluator_freeze": True,
            "engineering_pilot_ready": engineering_pilot_ready,
            "paper_release_ready": False,
            "pilot_allowed": engineering_pilot_ready,
            "pilot_status": "provisional_ai_assisted_annotations" if engineering_pilot_ready else "blocked",
            "pilot_blocker": "" if engineering_pilot_ready else "Engineering gates are incomplete.",
            "paper_release_blocker": (
                "Behavior, closure, taxonomy, duplicate, and workload records remain AI-assisted or "
                "unverified and therefore do not satisfy independent-human paper-release gates."
            ),
        },
    }
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    behavior = payload["behavior_contracts"]
    closure = payload["diagnostic_closure_gold"]
    taxonomy = payload["taxonomy"]
    week1 = payload["week1_execution"]
    preflight = payload["control_preflight"]
    duplicate_review = payload["near_duplicate_review"]
    # Release and Pilot are downstream/runtime state. Keep them out of OUTPUT_JSON,
    # which is itself a release-gate input, to avoid a hash dependency cycle.
    release = {
        "passed_gate_count": release_gate.get("passed_gate_count"),
        "gate_count": release_gate.get("gate_count"),
        "paper_release_ready": release_gate.get("paper_release_ready"),
        "engineering_pilot_ready": release_gate.get("engineering_pilot_ready"),
        "pilot_freeze_ready": release_gate.get("pilot_freeze_ready"),
    }
    pilot = {
        "freeze_id": pilot_freeze.get("freeze_id"),
        "pilot_revision": pilot_freeze.get("pilot_revision"),
        "evidence_status": pilot_freeze.get("evidence_status"),
        "execution_authorization_status": pilot_authorization.get("status"),
        "stage_a_planned_cell_count": pilot_authorization.get("stage_a_planned_cell_count"),
        "stage_a_launched_cell_count": pilot_authorization.get("stage_a_launched_cell_count"),
        "external_data_sent_by_stage_a_attempt": pilot_authorization.get(
            "external_data_sent_by_stage_a_attempt"
        ),
    }
    lines = [
        "# FeatureLiftBench v1.1 implementation status (generated)",
        "",
        "> This file reports repository state; auto-generated scaffolds are not human-reviewed gold.",
        "",
        "| Area | Current state | Complete? |",
        "| --- | ---: | :---: |",
        f"| Python tasks / TASK.md | {len(task_dirs)} / {payload['task_docs']['present']} | {'yes' if not missing_task_docs else 'no'} |",
        f"| Behavior contracts | {sum(contract_status.values())}/150 | yes (AI-assisted, provisional) |",
        f"| Public test mappings / unmapped | {public_total} / {public_unmapped} | {'yes' if public_unmapped == 0 else 'no'} |",
        f"| Hidden nodeid mappings / unmapped | {hidden_total} / {hidden_unmapped} | {'yes' if hidden_unmapped == 0 else 'no'} |",
        f"| Human-reviewed behavior tasks | {150 - len(contract_review_queue)}/150 | {'yes' if not contract_review_queue else 'no'} |",
        f"| Diagnostic file closure marked complete | {file_completeness.get('complete', 0)}/40 | yes (AI-assisted, provisional) |",
        f"| Diagnostic closure independently adjudicated | {40 - len(closure_review_queue)}/40 | {'yes' if not closure_review_queue else 'no'} |",
        f"| Taxonomy unresolved / pending human adjudication | {len(taxonomy_queue)} / {len(taxonomy_human_adjudication_queue)} | {'yes' if not taxonomy_human_adjudication_queue else 'no'} |",
        f"| Hard50 `split_role` | {hard_role_count}/50 | {'yes' if hard_role_count == 50 else 'no'} |",
        f"| Oracle canary | {week1['oracle_canary_run_count']}/15 | {'yes' if week1['oracle_canary_gate_pass'] else 'no'} |",
        f"| Full Oracle results | {week1['oracle_full_run_count']}/450 | {'yes' if week1['oracle_full_run_count'] == 450 else 'no'} |",
        f"| Stable Oracle pass / quarantine | {week1['oracle_stable_pass_task_count']} / {week1['oracle_quarantined_task_count']} | {'yes' if week1['oracle_unstable_task_count'] == 0 and week1['oracle_incomplete_task_count'] == 0 else 'no'} |",
        f"| Representative-20 quarantined | {len(week1['representative20_quarantined_task_ids'])} | {'yes' if not week1['representative20_quarantined_task_ids'] else 'no'} |",
        f"| Challenge-20 quarantined | {len(week1['challenge20_quarantined_task_ids'])} | {'yes' if not week1['challenge20_quarantined_task_ids'] else 'no'} |",
        f"| Historical infra re-eval | {week1['historical_infra_new_result_count']}/62; new infra failures {week1['historical_infra_new_failure_count']} | {'yes' if week1['historical_infra_reevaluation_gate_pass'] else 'no'} |",
        f"| Historical output hash mismatches | {week1['historical_output_hash_mismatch_count']} | {'yes' if week1['historical_output_hash_mismatch_count'] == 0 else 'no'} |",
        f"| Two-task control functional gate | {preflight['automated_functional_gate_passed']} | {'yes' if preflight['automated_functional_gate_passed'] else 'no'} |",
        f"| Two-task workload gate | {preflight['workload_gate_status']} | no |",
        f"| Near-duplicate semantic review | {duplicate_review['candidate_cluster_count'] - duplicate_review['needs_review_count']}/{duplicate_review['candidate_cluster_count']} | {'yes' if duplicate_review['needs_review_count'] == 0 else 'no'} |",
        f"| Paper release gates | {release['passed_gate_count']}/{release['gate_count']} | {'yes' if release['paper_release_ready'] else 'no'} |",
        f"| Engineering Pilot / freeze ready | {release['engineering_pilot_ready']} / {release['pilot_freeze_ready']} | {'yes' if release['engineering_pilot_ready'] and release['pilot_freeze_ready'] else 'no'} |",
        f"| Pilot freeze | revision {pilot['pilot_revision']} / `{pilot['freeze_id']}` | {'yes' if pilot['freeze_id'] else 'no'} |",
        f"| Stage A launched | {pilot['stage_a_launched_cell_count']}/{pilot['stage_a_planned_cell_count']} | no |",
        "",
        "## Review queues",
        "",
        f"- Behavior contract: {behavior['human_review_queue_count']} tasks; {hidden_unmapped} hidden and {public_unmapped} public nodeids remain unmapped.",
        f"- Closure gold: file scope is marked complete for {file_completeness.get('complete', 0)}/40, but {closure['human_review_queue_count']}/40 still await independent human review/adjudication; symbol/runtime/minimality claims remain scope-limited.",
        f"- Taxonomy: {taxonomy['needs_review_count']} tasks remain `needs_review`; {taxonomy['human_adjudication_queue_count']} AI-assisted rows still require human adjudication for paper release.",
        f"- Representative-20 contains quarantined tasks: {', '.join(week1['representative20_quarantined_task_ids']) or 'none'}.",
        f"- Challenge-20 contains quarantined tasks: {', '.join(week1['challenge20_quarantined_task_ids']) or 'none'}.",
        f"- Near-duplicate candidate clusters awaiting semantic review: {duplicate_review['needs_review_count']}.",
        f"- Pilot engineering assets are frozen at revision {pilot['pilot_revision']} (`{pilot['freeze_id']}`) with evidence status `{pilot['evidence_status']}`.",
        f"- Pilot execution status is `{pilot['execution_authorization_status']}`; Stage A has launched {pilot['stage_a_launched_cell_count']}/{pilot['stage_a_planned_cell_count']} cells and sent external data: {pilot['external_data_sent_by_stage_a_attempt']}.",
        "",
        "## Interpretation boundary",
        "",
        f"The frozen Oracle evidence supports evaluator stability for {week1['oracle_stable_pass_task_count']} stable tasks"
        f" and {week1['oracle_quarantined_task_count']} versioned quarantine tasks."
        " AI-assisted behavior, closure, taxonomy, and duplicate review artifacts are suitable for engineering Pilot diagnostics but do not satisfy independent-human paper-release criteria. Pilot execution additionally requires explicit authorization for the wider external export scope.",
        "",
    ]
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUTPUT_JSON.relative_to(ROOT)} and {OUTPUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
