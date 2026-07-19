#!/usr/bin/env python3
"""Validate structural integrity of behavior contracts and Diagnostic-40 closure annotations."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools/research_analysis"
sys.path.insert(0, str(TOOLS))

from materialize_v11_audit_assets import pytest_nodeids  # noqa: E402


TASKS = ROOT / "benchmark/tasks"
SUBSET = ROOT / "artifacts/research_analysis/v1_1/diagnostic_subset_manifest.json"
OUTPUT = ROOT / "artifacts/research_analysis/v1_1/annotation_integrity_report.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def evidence_file(task: Path, raw: str) -> Path:
    value = raw.split("#", 1)[0]
    return task / value


def main() -> int:
    subset = load(SUBSET)
    diagnostic = set(subset["representative_20"]) | set(subset["challenge_20"])
    errors: list[dict[str, str]] = []
    behavior_count = closure_count = 0
    for task in sorted(path for path in TASKS.iterdir() if (path / "metadata.json").is_file()):
        behavior = load(task / "evaluation/behavior_contract.json")
        behavior_count += 1
        clauses = {str(row.get("behavior_id")) for row in behavior.get("public_clauses") or [] if isinstance(row, dict)}
        task_hash = hashlib.sha256((task / "TASK.md").read_bytes()).hexdigest()
        if behavior.get("spec_sha256") != task_hash:
            errors.append({"task_id": task.name, "scope": "behavior", "error": "spec_sha256 drift"})
        for key, test_dir in (("public_test_mappings", "public_tests"), ("hidden_test_mappings", "hidden_tests")):
            mappings = behavior.get(key) or []
            mapped_nodeids = {str(row.get("nodeid")) for row in mappings if isinstance(row, dict)}
            actual_nodeids = set(pytest_nodeids(task / test_dir, task))
            if mapped_nodeids != actual_nodeids:
                errors.append({"task_id": task.name, "scope": "behavior", "error": f"{key} nodeid inventory drift"})
            for row in mappings:
                if not isinstance(row, dict):
                    continue
                unknown = set(row.get("public_clause_ids") or []) - clauses
                if unknown:
                    errors.append({"task_id": task.name, "scope": "behavior", "error": f"unknown clause ids: {sorted(unknown)}"})

        if task.name not in diagnostic:
            continue
        closure_count += 1
        closure = load(task / "evaluation/closure_gold.json")
        review = closure.get("review") if isinstance(closure.get("review"), dict) else {}
        status = review.get("status")
        if status in {"double_reviewed", "adjudicated"} and not (
            review.get("reviewer_1") and review.get("reviewer_2")
        ):
            errors.append({"task_id": task.name, "scope": "closure", "error": "double review lacks reviewer identities"})
        if status == "adjudicated" and (review.get("disagreements") or []) and not review.get("adjudicator"):
            errors.append({"task_id": task.name, "scope": "closure", "error": "disagreements lack adjudicator"})
        for variant in closure.get("closure_variants") or []:
            for requirement in variant.get("requirements") or []:
                for raw in requirement.get("evidence_paths") or []:
                    if not evidence_file(task, str(raw)).exists():
                        errors.append({"task_id": task.name, "scope": "closure", "error": f"missing evidence path: {raw}"})
                for solution in requirement.get("satisfied_by") or []:
                    if not isinstance(solution, dict):
                        continue
                    for artifact in solution.get("artifacts") or []:
                        if not isinstance(artifact, dict) or artifact.get("kind") != "file":
                            continue
                        raw = str(artifact.get("source_path") or "")
                        if raw and not (task / raw).exists():
                            errors.append({"task_id": task.name, "scope": "closure", "error": f"missing source artifact: {raw}"})
    payload = {
        "schema_version": "featureliftbench.annotation_integrity_report.v1",
        "behavior_contract_count": behavior_count,
        "diagnostic_closure_count": closure_count,
        "error_count": len(errors),
        "integrity_gate_pass": behavior_count == 150 and closure_count == 40 and not errors,
        "errors": errors,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("behavior_contract_count", "diagnostic_closure_count", "error_count", "integrity_gate_pass")}, indent=2))
    return 0 if payload["integrity_gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
