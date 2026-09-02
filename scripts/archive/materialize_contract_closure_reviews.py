#!/usr/bin/env python3
"""Expand concise reviewed decisions into per-test closure review ledgers."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "harness"
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))

from featureliftbench.contract_closure_audit import (  # noqa: E402
    REVIEW_SCHEMA,
    validate_review,
)


DEFAULT_AUDIT = ROOT / "reports/contract_closure_200/machine_audit.json"
DEFAULT_DECISIONS = ROOT / "reports/contract_closure_200/decisions.jsonl"
DEFAULT_OUTPUT = ROOT / "reports/contract_closure_200/reviews"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--decisions", type=Path, default=DEFAULT_DECISIONS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def load_decisions(path: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict) or not isinstance(value.get("task_id"), str):
            raise ValueError(f"{path}:{number}: decision must have task_id")
        task_id = str(value["task_id"])
        if task_id in result:
            raise ValueError(f"{path}:{number}: duplicate task_id {task_id}")
        result[task_id] = value
    return result


def component(value: Any, default_evidence: list[str]) -> dict[str, Any]:
    if isinstance(value, str):
        return {"verdict": value, "evidence": default_evidence, "issues": []}
    if isinstance(value, dict):
        return {
            "verdict": value.get("verdict"),
            "evidence": value.get("evidence") or default_evidence,
            "issues": value.get("issues") or [],
        }
    return {"verdict": "pending", "evidence": [], "issues": []}


def materialize(task: dict[str, Any], decision: dict[str, Any]) -> dict[str, Any]:
    default_verdict = decision.get("default_test_verdict")
    default_evidence = [str(value) for value in decision.get("default_evidence_basis") or []]
    overrides = decision.get("test_overrides") if isinstance(decision.get("test_overrides"), dict) else {}
    tests = []
    for test in task.get("tests") or []:
        override = overrides.get(test["nodeid"])
        override = override if isinstance(override, dict) else {}
        behavior_ids = override.get("behavior_ids")
        if behavior_ids is None:
            behavior_ids = test.get("behavior_ids") or []
        evidence = override.get("evidence_basis")
        if evidence is None:
            evidence = [f"public_spec:{value}" for value in behavior_ids] or default_evidence
        tests.append(
            {
                "nodeid": test["nodeid"],
                "behavior_ids": behavior_ids,
                "verdict": override.get("verdict", default_verdict),
                "evidence_basis": evidence,
                "notes": override.get("notes", "Reviewed against the task dossier and pinned evidence."),
            }
        )
    component_evidence = default_evidence or ["task_dossier", "pinned_task_evidence"]
    raw_components = decision.get("components") if isinstance(decision.get("components"), dict) else {}
    return {
        "schema_version": REVIEW_SCHEMA,
        "task_id": task["task_id"],
        "review_status": decision.get("review_status", "ai_assisted_reviewed"),
        "reviewer": decision.get("reviewer", "codex_contract_closure_pass_20260804"),
        "reviewed_at": decision.get("reviewed_at", "2026-08-04"),
        "oracle_relation": decision.get("oracle_relation"),
        "components": {
            name: component(raw_components.get(name), component_evidence)
            for name in ("api_surface", "behavior", "dependency_environment")
        },
        "tests": tests,
        "overall_verdict": decision.get("overall_verdict"),
        "revision_required": decision.get("revision_required"),
        "issues": decision.get("issues") or [],
        "notes": decision.get("notes", ""),
    }


def main() -> int:
    args = parse_args()
    audit_path = args.audit if args.audit.is_absolute() else ROOT / args.audit
    decisions_path = args.decisions if args.decisions.is_absolute() else ROOT / args.decisions
    output = args.output if args.output.is_absolute() else ROOT / args.output
    audit = load_object(audit_path)
    tasks = {str(value["task_id"]): value for value in audit.get("tasks") or []}
    decisions = load_decisions(decisions_path)
    unknown = set(decisions) - set(tasks)
    if unknown:
        raise SystemExit(f"unknown decision task ids: {', '.join(sorted(unknown))}")
    output.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []
    for task_id, decision in decisions.items():
        review = materialize(tasks[task_id], decision)
        errors = validate_review(review, tasks[task_id])
        if errors:
            failures.append(f"{task_id}: {'; '.join(errors[:5])}")
            continue
        path = output / f"{task_id}.json"
        rendered = json.dumps(review, indent=2, sort_keys=True) + "\n"
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != rendered:
                failures.append(f"{task_id}: materialized review is stale or missing")
        else:
            path.write_text(rendered, encoding="utf-8")
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    print(f"Materialized {len(decisions)} reviewed decisions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
