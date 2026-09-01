#!/usr/bin/env python3
"""Build or verify the Python-150 compatibility view of Python-200-prime.

The runtime still uses the historical v3 freeze interface for tasks in
``benchmark/tasks``.  After those 150 task contracts were hardened for the
Python-200-prime release, the old v3 manifest no longer matched their spec
hashes.  This script projects the Python-150 stratum from the immutable
Python-200 candidate and attaches the unified 600/600 Oracle evidence without
changing the frozen evaluator or the Python-200 candidate identity.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "harness"
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))

from featureliftbench.freeze import (  # noqa: E402
    file_manifest,
    manifest_digest,
    sha256_file,
)


SCHEMA_VERSION = "featureliftbench.benchmark_freeze.v3"
POLICY_ID = "featureliftbench.full_repository_no_hint_main.v3"
SOURCE_POLICY_ID = "featureliftbench.full_repository_source.v2"
DEFAULT_CANDIDATE = (
    ROOT
    / "artifacts"
    / "research_analysis"
    / "python200_prime"
    / "current_candidate_freeze.json"
)
DEFAULT_FINAL = (
    ROOT
    / "artifacts"
    / "research_analysis"
    / "python200_prime"
    / "current_benchmark_freeze.json"
)
DEFAULT_ORACLE = (
    ROOT
    / "reports"
    / "audits"
    / "python200_prime_oracle_revalidation"
    / "summary.json"
)
DEFAULT_COMPACTNESS = (
    ROOT / "benchmark" / "references" / "python200_prime_compactness.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "artifacts"
    / "research_analysis"
    / "v3"
    / "current_benchmark_freeze.json"
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--final-freeze", type=Path, default=DEFAULT_FINAL)
    parser.add_argument("--oracle-report", type=Path, default=DEFAULT_ORACLE)
    parser.add_argument("--compactness", type=Path, default=DEFAULT_COMPACTNESS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def _candidate_digest(payload: dict[str, Any]) -> str:
    normalized = dict(payload)
    normalized.pop("candidate_id", None)
    return manifest_digest(normalized)


def _tree_digest(path: Path) -> dict[str, Any]:
    resolved = path.resolve()
    files = file_manifest([resolved], root=resolved)
    return {"sha256": manifest_digest({"files": files}), "file_count": len(files)}


def _validate_sources(
    candidate: dict[str, Any],
    final_freeze: dict[str, Any],
    oracle: dict[str, Any],
    compactness: dict[str, Any],
) -> tuple[list[str], dict[str, dict[str, Any]]]:
    candidate_id = candidate.get("candidate_id")
    if (
        candidate.get("schema_version")
        != "featureliftbench.python200_prime_candidate_freeze.v1"
        or candidate_id != _candidate_digest(candidate)
        or candidate.get("task_count") != 200
    ):
        raise ValueError("Python-200 candidate is invalid")
    if (
        final_freeze.get("schema_version")
        != "featureliftbench.python200_prime_benchmark_freeze.v1"
        or final_freeze.get("candidate_id") != candidate_id
        or final_freeze.get("gate_pass") is not True
        or final_freeze.get("freeze_id") != manifest_digest(final_freeze)
    ):
        raise ValueError("Python-200 final freeze is invalid or mismatched")
    oracle_summary = oracle.get("summary") or {}
    if (
        oracle.get("schema_version")
        != "featureliftbench.python200_prime_oracle_revalidation.v1"
        or oracle.get("candidate_id") != candidate_id
        or oracle.get("gate_pass") is not True
        or oracle_summary.get("task_count") != 200
        or oracle_summary.get("expected_runs") != 600
        or oracle_summary.get("passed_runs") != 600
        or oracle_summary.get("stable_tasks") != 200
        or oracle.get("failed_task_ids")
        or oracle.get("unstable_task_ids")
    ):
        raise ValueError("unified Oracle evidence is not 600/600 for this candidate")
    compactness_tasks = compactness.get("tasks")
    if (
        compactness.get("schema_version")
        != "featureliftbench.compactness_reference.v1"
        or compactness.get("task_count") != 200
        or not isinstance(compactness_tasks, dict)
    ):
        raise ValueError("Python-200 compactness registry is invalid")

    candidate_tasks = candidate.get("tasks")
    if not isinstance(candidate_tasks, dict):
        raise ValueError("candidate task records are missing")
    task_ids = sorted(
        task_id
        for task_id, record in candidate_tasks.items()
        if isinstance(record, dict) and record.get("stratum") == "python150"
    )
    if len(task_ids) != 150:
        raise ValueError(f"expected 150 Python-150 records, found {len(task_ids)}")
    if set(task_ids) != set(compactness_tasks).intersection(task_ids):
        raise ValueError("compactness registry does not cover the Python-150 stratum")

    run_counts = {task_id: 0 for task_id in task_ids}
    for run in oracle.get("runs") or []:
        if not isinstance(run, dict):
            continue
        task_id = run.get("task_id")
        if task_id in run_counts:
            if run.get("passed") is not True:
                raise ValueError(f"{task_id}: selected Oracle run failed")
            run_counts[task_id] += 1
    bad_counts = {task_id: count for task_id, count in run_counts.items() if count != 3}
    if bad_counts:
        raise ValueError(f"selected Oracle repetitions are incomplete: {list(bad_counts.items())[:3]}")
    return task_ids, compactness_tasks


def build_payload(
    candidate_path: Path,
    final_path: Path,
    oracle_path: Path,
    compactness_path: Path,
) -> dict[str, Any]:
    candidate = _load(candidate_path)
    final_freeze = _load(final_path)
    oracle = _load(oracle_path)
    compactness = _load(compactness_path)
    task_ids, compactness_tasks = _validate_sources(
        candidate, final_freeze, oracle, compactness
    )
    candidate_tasks = candidate["tasks"]

    tasks: dict[str, dict[str, Any]] = {}
    for task_id in task_ids:
        source = candidate_tasks[task_id]
        reference = compactness_tasks[task_id]
        if reference.get("reference_tree_sha256") != (
            source.get("reference_tree") or {}
        ).get("sha256"):
            raise ValueError(f"{task_id}: compactness reference tree mismatch")
        record = dict(source)
        record.pop("stratum", None)
        record.pop("reference_kind", None)
        record["compactness_reference"] = reference
        tasks[task_id] = record

    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "policy_id": POLICY_ID,
        "source_policy_id": SOURCE_POLICY_ID,
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "split": "python-external-main-150",
        "curated_split": "python-curated-7",
        "task_count": 150,
        "curated_task_count": 7,
        "gate_pass": True,
        "primary_metric": "functional_pass_at_1",
        "functional_definition": "Build AND Public AND Hidden AND Isolation",
        "agent_condition": candidate.get("agent_condition"),
        "evaluation_condition": candidate.get("evaluation_condition"),
        "environment": {"images": final_freeze.get("images")},
        "gates": {
            "task_validation": 150,
            "oracle_runs_passed": 450,
            "oracle_tasks_stable": 150,
            "compatibility_projection": True,
        },
        "oracle_revalidation": {
            "path": _relative(oracle_path),
            "sha256": sha256_file(oracle_path),
            "schema_version": oracle.get("schema_version"),
            "candidate_id": candidate.get("candidate_id"),
            "selected_summary": {
                "task_count": 150,
                "repetitions": 3,
                "expected_runs": 450,
                "passed_runs": 450,
                "stable_tasks": 150,
            },
        },
        "compactness_reference_registry": {
            "path": _relative(compactness_path),
            "sha256": sha256_file(compactness_path),
            "registry_id": compactness.get("registry_id"),
            "task_count": compactness.get("task_count"),
        },
        "compatibility_source": {
            "purpose": "runtime bridge for the Python-150 stratum after Python-200 contract hardening",
            "candidate_path": _relative(candidate_path),
            "candidate_id": candidate.get("candidate_id"),
            "final_freeze_path": _relative(final_path),
            "final_freeze_id": final_freeze.get("freeze_id"),
            "projection_only": True,
        },
        "tasks": tasks,
    }
    payload["freeze_id"] = manifest_digest(payload)
    return payload


def verify_existing(
    payload: dict[str, Any],
    candidate_path: Path,
    final_path: Path,
    oracle_path: Path,
    compactness_path: Path,
) -> None:
    if (
        payload.get("schema_version") != SCHEMA_VERSION
        or payload.get("policy_id") != POLICY_ID
        or payload.get("source_policy_id") != SOURCE_POLICY_ID
        or payload.get("task_count") != 150
        or payload.get("gate_pass") is not True
        or payload.get("freeze_id") != manifest_digest(payload)
    ):
        raise ValueError("compatibility freeze identity is invalid")

    candidate = _load(candidate_path)
    final_freeze = _load(final_path)
    oracle = _load(oracle_path)
    compactness = _load(compactness_path)
    task_ids, _ = _validate_sources(candidate, final_freeze, oracle, compactness)
    source = payload.get("compatibility_source") or {}
    if (
        source.get("candidate_id") != candidate.get("candidate_id")
        or source.get("final_freeze_id") != final_freeze.get("freeze_id")
    ):
        raise ValueError("compatibility source identity drifted")
    evidence = payload.get("oracle_revalidation") or {}
    if evidence.get("sha256") != sha256_file(oracle_path):
        raise ValueError("Oracle evidence drifted")
    reference = payload.get("compactness_reference_registry") or {}
    if reference.get("sha256") != sha256_file(compactness_path):
        raise ValueError("compactness registry drifted")

    records = payload.get("tasks")
    if not isinstance(records, dict) or set(records) != set(task_ids):
        raise ValueError("compatibility task membership drifted")
    for task_id in task_ids:
        record = records[task_id]
        candidate_record = candidate["tasks"][task_id]
        for field in (
            "task_revision",
            "spec_hash",
            "generated_task_hash",
            "source_snapshot_id",
            "source_tree_sha256",
            "source_archive_sha256",
        ):
            if record.get(field) != candidate_record.get(field):
                raise ValueError(f"{task_id}: {field} drifted from Python-200 candidate")
        if _tree_digest(ROOT / "benchmark" / "tasks" / task_id) != record.get(
            "task_tree"
        ):
            raise ValueError(f"{task_id}: task tree drifted")


def main() -> int:
    args = _parse_args()
    candidate_path = args.candidate.resolve()
    final_path = args.final_freeze.resolve()
    oracle_path = args.oracle_report.resolve()
    compactness_path = args.compactness.resolve()
    output = args.output.resolve()
    if args.check:
        payload = _load(output)
        verify_existing(
            payload, candidate_path, final_path, oracle_path, compactness_path
        )
        print(f"Verified Python-150 compatibility freeze: {payload['freeze_id']}")
        return 0

    payload = build_payload(
        candidate_path, final_path, oracle_path, compactness_path
    )
    immutable = output.parent / "freezes" / f"{payload['freeze_id']}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    immutable.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if immutable.exists():
        existing = _load(immutable)
        if existing.get("freeze_id") != payload["freeze_id"]:
            raise ValueError(f"immutable freeze collision: {immutable}")
    else:
        shutil.copy2(output, immutable)
    verify_existing(payload, candidate_path, final_path, oracle_path, compactness_path)
    print(f"Wrote Python-150 compatibility freeze: {payload['freeze_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
