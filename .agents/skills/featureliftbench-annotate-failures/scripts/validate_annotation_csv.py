#!/usr/bin/env python3
"""Validate a FeatureLiftBench failure-root-cause annotation CSV."""
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path

VALID_CAUSES = {
    "agent_process_non_delivery",
    "localization",
    "contract_api_completion",
    "dependency_closure",
    "behavior_drift",
    "packaging_modularization",
    "test_gaming_narrow",
    "task_or_evaluator_defect",
    "unknown",
}

VALIDITY = {
    "",
    "benchmark_invalid_candidate",
    "evidence_unavailable",
    "infrastructure_invalid",
    "policy_noncompliant",
}

REQUIRED = {
    "task_id",
    "model",
    "root_cause_primary",
    "secondary_tags",
    "contract_clause_ids",
    "evidence_summary",
    "evidence_path",
    "review_status",
    "first_failure_stage",
    "evidence_eligibility",
}

LEAK = re.compile(r"hidden_tests/|test_hidden|::test_")
CLAUSE = re.compile(r"^B[0-9]{3}$")
CLOSURE = {"contract_api_completion", "dependency_closure", "behavior_drift"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    args = parser.parse_args()
    with args.csv_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        print("empty CSV", file=sys.stderr)
        return 1
    missing_fields = sorted(REQUIRED - set(rows[0]))
    if missing_fields:
        print(f"missing fields: {missing_fields}", file=sys.stderr)
        return 1
    errors: list[str] = []
    seen: set[tuple[str, str]] = set()
    for i, row in enumerate(rows, start=2):
        key = (row.get("model", "").strip(), row["task_id"].strip())
        if key in seen:
            errors.append(f"L{i}: duplicate {key}")
        seen.add(key)
        cause = row["root_cause_primary"].strip()
        if cause not in VALID_CAUSES:
            errors.append(f"L{i} {key}: bad cause {cause!r}")
        override = (row.get("validity_override") or "").strip()
        if override not in VALIDITY:
            errors.append(f"L{i} {key}: bad validity_override {override!r}")
        eligibility = (row.get("evidence_eligibility") or "").strip()
        if cause == "task_or_evaluator_defect" and override != "benchmark_invalid_candidate":
            errors.append(f"L{i} {key}: defect requires benchmark_invalid_candidate")
        if override == "benchmark_invalid_candidate" and cause != "task_or_evaluator_defect":
            errors.append(f"L{i} {key}: override/cause mismatch")
        if eligibility == "benchmark_invalid_candidate" and cause != "task_or_evaluator_defect":
            errors.append(f"L{i} {key}: eligibility/cause mismatch")
        clauses = (row.get("contract_clause_ids") or "").strip()
        if clauses and any(CLAUSE.fullmatch(part) is None for part in clauses.split(";")):
            errors.append(f"L{i} {key}: bad clauses {clauses!r}")
        public = " ".join(
            [
                row.get("evidence_summary") or "",
                row.get("validity_reason") or "",
                row.get("secondary_tags") or "",
            ]
        )
        if LEAK.search(public):
            errors.append(f"L{i} {key}: Hidden identifier leak")
        if not (row.get("evidence_summary") or "").strip():
            errors.append(f"L{i} {key}: empty evidence_summary")
        if not (row.get("review_status") or "").strip():
            errors.append(f"L{i} {key}: empty review_status")
    if errors:
        print("\n".join(errors[:50]), file=sys.stderr)
        if len(errors) > 50:
            print(f"... {len(errors) - 50} more", file=sys.stderr)
        return 1
    valid = [
        row
        for row in rows
        if (row.get("evidence_eligibility") or "").strip() == "valid_agent_evidence"
    ]
    defects = [
        row
        for row in rows
        if (row.get("evidence_eligibility") or "").strip() == "benchmark_invalid_candidate"
    ]
    causes = Counter(row["root_cause_primary"] for row in valid)
    closure = sum(causes[name] for name in CLOSURE)
    print(
        {
            "n": len(rows),
            "valid_agent": len(valid),
            "defects": len(defects),
            "causes": dict(sorted(causes.items())),
            "closure_n": closure,
            "localization_n": causes["localization"],
            "unknown_n": causes["unknown"],
            "review_status": dict(Counter(row["review_status"] for row in rows)),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
