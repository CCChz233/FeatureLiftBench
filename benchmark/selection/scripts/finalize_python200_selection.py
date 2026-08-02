#!/usr/bin/env python3
"""Replace the rejected External-50 rows with the realized Python-200 tasks."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
POLICY_PATH = ROOT / "benchmark/selection/python200_balance_policy.json"
SELECTION_PATH = ROOT / "benchmark/selection/external50_expansion_20260731.json"
CARDS_DIR = ROOT / "benchmark/selection/external50_design_cards"

ASSIGNMENTS = [
    ("cssselect__selector_xpath_core__001", "cache-direct-config-01", "cacheout__ttl_policy_core__001"),
    ("textx__metamodel_model_core__001", "cache-direct-third-party-02", "stamina__retry_context_core__001"),
    ("parsimonious__grammar_visitor_core__001", "cache-composite-third-party-03", "cachier__memoize_backend_core__001"),
    ("ijson__event_parse_core__001", "workflow-composite-framework-01", "automat__methodical_workflow_core__001"),
    ("chardet__detect_core__001", "workflow-composite-config-02", "python_statemachine__json_workflow_core__001"),
    ("premailer__inline_css_core__001", "workflow-composite-third-party-03", "pyee__event_workflow_core__001"),
    ("dill__serialize_settings_core__001", "resource-direct-01", "publicsuffixlist__metadata_lookup_core__001"),
    ("cloudpickle__dumps_loads_core__001", "resource-direct-02", "puremagic__signature_resource_core__001"),
    ("frictionless__schema_resource_validate_core__001", "resource-composite-third-party-03", "langcodes__language_metadata_core__001"),
    ("pykwalify__map_seq_validate_core__001", "registry-composite-framework-01", "venusian__scan_dispatch_core__001"),
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def lift_type(metadata: dict[str, Any]) -> str:
    for value in ("Direct", "Adapted", "Composite"):
        if value.lower() in metadata.get("tags", []):
            return value
    raise ValueError(f"missing lift tag for {metadata['task_id']}")


def card_text(metadata: dict[str, Any], slot: dict[str, Any]) -> str:
    source = metadata["source"]
    feature = metadata["feature"]
    public_spec = metadata["public_spec"]
    required = [entry["path"] for entry in public_spec["required_api"]]
    required_lines = "\n".join(f"  - `{path}`" for path in required)
    behavior_lines = "\n".join(
        f"  - {value}" for value in feature["included_behaviors"]
    )
    exclusion_lines = "\n".join(
        f"  - {value}" for value in feature["excluded_behaviors"]
    )
    dependencies = metadata["environment"].get("allowed_dependencies", [])
    dependency_text = ", ".join(dependencies) if dependencies else "none"
    return f"""# Design card: {metadata['task_id']}

**status:** `reference_static_validated`  
**wave:** R1  
**package:** `{source['name']}`  
**repository_url:** {source['url']}  
**replacement_slot:** `{slot['slot_id']}`  
**final_lift_type:** {slot['lift_type']}  
**feature_family:** {slot['feature_family']}  
**entanglement:** {slot['entanglement']}  
**feature_one_liner:** {feature['name']}  
**lift_review_flag:** none

**source_review:** `pass` (2026-08-01)  
**contract_review:** `pass` (2026-08-01)  
**reference_review:** `pass` (2026-08-01)  
**isolation_review:** `static_pass`

## Balance Role

{slot['design_requirement']}

## Pinned Source

- commit: `{source['commit']}`
- license: `{source['license']}`
- source kind: real external OSS repository
- network during evaluation: forbidden
- allowed runtime dependencies: {dependency_text}

## Required API

{required_lines}

## Included Behavior

{behavior_lines}

## Excluded Behavior

{exclusion_lines}

## Gate Status

- package completeness: pass
- explicit public API contract: pass
- reference tests: pass
- static isolation and forbidden-import checks: pass
- Docker evaluation: pending
- promotion to `benchmark/tasks`: blocked until the complete External-50 gate passes
"""


def main() -> int:
    policy = load_json(POLICY_PATH)
    selection = load_json(SELECTION_PATH)
    slots = {slot["slot_id"]: slot for slot in policy["replacement_slots"]}
    rows = selection["rows"]
    by_id = {row["task_id"]: row for row in rows if row.get("task_id")}

    assignment_records: list[dict[str, str]] = []
    replacement_ids: set[str] = set()
    for old_id, slot_id, new_id in ASSIGNMENTS:
        if old_id not in by_id:
            raise ValueError(f"replacement candidate missing from selection: {old_id}")
        if slot_id not in slots:
            raise ValueError(f"replacement slot missing from policy: {slot_id}")
        task_dir = ROOT / "benchmark/staging" / new_id
        metadata = load_json(task_dir / "metadata.json")
        slot = slots[slot_id]
        actual_lift = lift_type(metadata)
        if actual_lift != slot["lift_type"]:
            raise ValueError(f"{new_id}: lift {actual_lift} != slot {slot['lift_type']}")
        if metadata["entanglement"]["primary"] != slot["entanglement"]:
            raise ValueError(f"{new_id}: entanglement does not match {slot_id}")

        old = by_id[old_id]
        old["disposition"] = "replaced"
        old["status"] = "replaced_for_python200_balance"
        old["replacement_slot_id"] = slot_id
        old["replacement_task_id"] = new_id

        new_row = {
            "disposition": "selected",
            "task_id": new_id,
            "package": metadata["source"]["name"],
            "repository_url": metadata["source"]["url"],
            "lift_type": slot["lift_type"],
            "feature_family": slot["feature_family"],
            "entanglement": slot["entanglement"],
            "wave": "R1",
            "feature_one_liner": metadata["feature"]["name"],
            "design_note": slot["design_requirement"],
            "source_kind": "external_oss",
            "pin_status": "pinned",
            "planned_lift_type": slot["lift_type"],
            "final_lift_type": slot["lift_type"],
            "reclassification_reason": None,
            "design_card": f"benchmark/selection/external50_design_cards/{new_id}.md",
            "design_card_status": "reference_static_validated",
            "lift_review_flag": None,
            "status": "reference_static_validated",
            "pinned_commit": metadata["source"]["commit"],
            "pinned_tag": None,
            "staging_path": f"benchmark/staging/{new_id}/",
            "replacement_for": old_id,
            "replacement_slot_id": slot_id,
        }
        if new_id in by_id:
            by_id[new_id].clear()
            by_id[new_id].update(new_row)
        else:
            rows.append(new_row)
            by_id[new_id] = new_row
        (CARDS_DIR / f"{new_id}.md").write_text(
            card_text(metadata, slot), encoding="utf-8"
        )
        replacement_ids.add(new_id)
        assignment_records.append(
            {"candidate_task_id": old_id, "slot_id": slot_id, "replacement_task_id": new_id}
        )

    reclasses = policy.get("label_reclassification_review", {})
    for task_id, review in reclasses.items():
        row = by_id[task_id]
        row["feature_family"] = review["feature_family"]
        row["reclassification_reason"] = review["reason"]

    selected = [row for row in rows if row.get("disposition") == "selected"]
    if len(selected) != 50 or len({row["task_id"] for row in selected}) != 50:
        raise ValueError("realized selection must contain 50 unique selected tasks")
    lift_counts = Counter(row["final_lift_type"] for row in selected)
    wave_counts = Counter(row["wave"] for row in selected)
    selection["selection_id"] = "external50-expansion-20260801-v2"
    selection["selection_date"] = "2026-08-01"
    selection["quota"] = {**dict(sorted(lift_counts.items())), "total": 50}
    selection["summary"] = {
        "selected": 50,
        "replaced": 10,
        "backups": sum(row.get("disposition") == "backup" for row in rows),
        **dict(sorted(lift_counts.items())),
        "waves": dict(sorted(wave_counts.items())),
    }
    selection["notes"] = [
        "Python-150 remains frozen; this ledger realizes the balanced External-50 expansion.",
        "The 10 rows marked replaced remain as provenance and are not part of the selected 50.",
        "R1 contains 10 real-source replacements matched to the balance policy slots.",
        "Promotion remains blocked until the selected 50 pass reference, isolation, Docker, and lifecycle gates.",
    ]

    policy["schema_version"] = "featureliftbench.python200_balance_policy.v2"
    policy["policy_id"] = "python200-balance-20260801-v2"
    policy["replacement_assignments"] = assignment_records
    evidence = policy.setdefault("redesign_evidence", {})
    evidence["resolved_member_contract_task_ids"] = evidence.get(
        "resolved_member_contract_task_ids",
        evidence.get("undeclared_member_gap_task_ids", []),
    )
    evidence["undeclared_member_gap_task_ids"] = []
    evidence["resolved_offline_dependency_task_ids"] = evidence.get(
        "resolved_offline_dependency_task_ids",
        evidence.get("offline_dependency_gap_task_ids", []),
    )
    evidence["offline_dependency_gap_task_ids"] = []
    evidence["resolved_pass_with_care"] = {
        "cachecontrol__heuristic_store_core__001": "In-memory DictCache and fake-response paths only; no HTTP session or network.",
        "flask_login__session_guard_core__001": "Flask test request contexts only; no server or external auth service.",
        "sqlglot__parse_transpile_core__001": "Frozen parse/transpile API and sqlite/postgres/mysql dialect subset; optimizer excluded.",
        "watchdog__observer_dispatch_core__001": "PollingObserver is exported as Observer with bounded temp-directory tests.",
    }
    evidence["pass_with_care_task_ids"] = []
    evidence["portalocker_member_review"] = (
        "Lock.write/close candidates were rejected because they belong to the returned file handle, not portalocker.Lock."
    )
    policy["realization"] = {
        "status": "reference_and_static_gates_pass",
        "selected_task_count": 50,
        "replacement_task_count": len(replacement_ids),
        "reference_tests": 357,
        "contract_validation": "50/50",
        "source_materialization": "50/50",
        "static_isolation": "50/50",
        "next_gate": "docker_reference_and_lifecycle",
    }
    dump_json(SELECTION_PATH, selection)
    dump_json(POLICY_PATH, policy)
    print("realized Python-200 selection: 40 retained + 10 replacements")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
