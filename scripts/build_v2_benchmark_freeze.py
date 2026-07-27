#!/usr/bin/env python3
"""Build and verify the Full-Repository / No-Hint Python-150 freeze."""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "harness"
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))

from featureliftbench.freeze import (
    file_manifest,
    manifest_digest,
    sha256_file,
    verify_file_manifest,
)
from featureliftbench.scoring import score_submission
from featureliftbench.source_archive import load_source_registry, source_indexes
from featureliftbench.task_spec import compute_generated_task_hash, compute_spec_hash
from featureliftbench.validate import validate_task


POLICY_ID = "featureliftbench.full_repository_no_hint_main.v2"
SOURCE_POLICY_ID = "featureliftbench.full_repository_source.v1"
SCHEMA_VERSION = "featureliftbench.benchmark_freeze.v2"
DEFAULT_ORACLE_REPORT = (
    ROOT / "reports" / "audits" / "v2_oracle_revalidation" / "summary.json"
)
DEFAULT_READINESS_REPORT = (
    ROOT / "reports" / "audits" / "v2_source_nohint_gate.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "artifacts"
    / "research_analysis"
    / "v2"
    / "current_benchmark_freeze.json"
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oracle-report", type=Path, default=DEFAULT_ORACLE_REPORT)
    parser.add_argument(
        "--readiness-report", type=Path, default=DEFAULT_READINESS_REPORT
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the current freeze against all frozen files and evidence",
    )
    return parser.parse_args()


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _tree_digest(path: Path) -> dict[str, Any]:
    files = file_manifest([path], root=path)
    return {
        "sha256": manifest_digest({"files": files}),
        "file_count": len(files),
    }


def _docker_identity(image: str) -> dict[str, str]:
    completed = subprocess.run(
        ["docker", "image", "inspect", image, "--format", "{{.Id}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "name": image,
        "id": completed.stdout.strip(),
    }


def _validate_scoring_semantics() -> dict[str, Any]:
    passing = score_submission(
        metrics={"loc": 200, "reference_loc": 100},
        metadata={},
        functional_gate_score=1.0,
    )
    failing = score_submission(
        metrics={"loc": 200, "reference_loc": 100},
        metadata={},
        functional_gate_score=0.0,
    )
    copy_all = score_submission(
        metrics={"loc": 10_000, "reference_loc": 100},
        metadata={},
        functional_gate_score=1.0,
    )
    gate_pass = (
        passing["final_score"] == passing["functional_gate"] == 1.0
        and failing["final_score"] == failing["functional_gate"] == 0.0
        and passing["compactness_score"] == failing["compactness_score"] == 0.5
        and copy_all["functional_gate"] == 1.0
        and copy_all["compactness_score"] <= 0.01
    )
    return {
        "gate_pass": gate_pass,
        "functional_primary_probe": passing,
        "functional_failure_probe": failing,
        "copy_all_probe": copy_all,
    }


def _verify_source_archives(registry: dict[str, Any]) -> dict[str, Any]:
    failures: list[dict[str, str]] = []
    verified = 0
    for snapshot in registry.get("snapshots", []):
        if not isinstance(snapshot, dict):
            continue
        snapshot_id = str(snapshot.get("source_snapshot_id") or "")
        archive_path = ROOT / str(snapshot.get("archive_path") or "")
        if snapshot.get("status") != "ready":
            failures.append({"snapshot_id": snapshot_id, "reason": "not ready"})
            continue
        if not archive_path.is_file():
            failures.append({"snapshot_id": snapshot_id, "reason": "archive missing"})
            continue
        actual = sha256_file(archive_path)
        expected = str(snapshot.get("archive_sha256") or "")
        if actual != expected:
            failures.append(
                {
                    "snapshot_id": snapshot_id,
                    "reason": f"archive digest mismatch: {actual} != {expected}",
                }
            )
            continue
        verified += 1
    return {
        "gate_pass": verified == 126 and not failures,
        "verified_snapshots": verified,
        "failures": failures,
    }


def build_payload(
    oracle_report_path: Path,
    readiness_report_path: Path,
) -> dict[str, Any]:
    oracle = _load(oracle_report_path)
    if (
        oracle.get("policy_id") != POLICY_ID
        or oracle.get("gate_pass") is not True
        or (oracle.get("summary") or {}).get("task_count") != 150
        or (oracle.get("summary") or {}).get("repetitions", 0) < 3
        or (oracle.get("summary") or {}).get("passed_runs") != 450
        or oracle.get("failed_task_ids")
        or oracle.get("unstable_task_ids")
    ):
        raise ValueError("v2 Oracle report has not passed the 150 x 3 gate")

    readiness = _load(readiness_report_path)
    readiness_summary = readiness.get("summary") or {}
    for key in ("contract_pass", "no_hint_pass", "full_repository_ready"):
        if readiness_summary.get(key) != 150:
            raise ValueError(f"readiness evidence does not have {key}=150")

    registry_path = ROOT / "benchmark" / "sources" / "registry.json"
    registry = load_source_registry(registry_path)
    if registry.get("policy_id") != SOURCE_POLICY_ID:
        raise ValueError("source registry policy does not match v2 source policy")
    registry_summary = registry.get("summary") or {}
    if (
        registry_summary.get("task_count") != 150
        or registry_summary.get("snapshot_count") != 126
        or registry_summary.get("ready_snapshot_count") != 126
        or registry_summary.get("pending_snapshot_count") != 0
    ):
        raise ValueError("canonical source registry is incomplete")
    _, task_snapshots = source_indexes(registry)
    source_verification = _verify_source_archives(registry)
    if not source_verification["gate_pass"]:
        raise ValueError(
            f"source archive verification failed: {source_verification['failures'][:3]}"
        )

    task_dirs = sorted(
        path
        for path in (ROOT / "benchmark" / "tasks").iterdir()
        if path.is_dir() and (path / "metadata.json").is_file()
    )
    if len(task_dirs) != 150:
        raise ValueError(f"expected 150 Python tasks, found {len(task_dirs)}")
    reference_registry_path = (
        ROOT / "benchmark" / "references" / "compactness.json"
    )
    reference_registry = _load(reference_registry_path)
    reference_tasks = reference_registry.get("tasks")
    if (
        reference_registry.get("task_count") != 150
        or not isinstance(reference_tasks, dict)
        or len(reference_tasks) != 150
    ):
        raise ValueError("compactness reference registry is incomplete")

    tasks: dict[str, dict[str, Any]] = {}
    for task_dir in task_dirs:
        task_id = task_dir.name
        metadata = _load(task_dir / "metadata.json")
        validation = validate_task(task_dir)
        if not validation.valid:
            raise ValueError(
                f"{task_id}: task validation failed: {'; '.join(validation.errors)}"
            )
        public_spec = metadata.get("public_spec")
        if not isinstance(public_spec, dict):
            raise ValueError(f"{task_id}: public_spec missing")
        task_markdown = (task_dir / "TASK.md").read_text(encoding="utf-8")
        spec_hash = compute_spec_hash(public_spec)
        generated_hash = compute_generated_task_hash(task_markdown)
        if metadata.get("spec_hash") != spec_hash:
            raise ValueError(f"{task_id}: spec hash mismatch")
        if metadata.get("generated_task_hash") != generated_hash:
            raise ValueError(f"{task_id}: generated TASK hash mismatch")
        snapshot = task_snapshots.get(task_id)
        if not isinstance(snapshot, dict) or snapshot.get("status") != "ready":
            raise ValueError(f"{task_id}: canonical source snapshot is not ready")
        oracle_dir = ROOT / "benchmark" / "submissions" / task_id / "oracle"
        if not oracle_dir.is_dir():
            raise ValueError(f"{task_id}: Oracle submission missing")
        oracle_tree = _tree_digest(oracle_dir)
        reference_record = reference_tasks.get(task_id)
        if (
            not isinstance(reference_record, dict)
            or reference_record.get("reference_tree_sha256")
            != oracle_tree.get("sha256")
        ):
            raise ValueError(f"{task_id}: compactness reference registry has drifted")
        tasks[task_id] = {
            "task_revision": metadata.get("task_revision"),
            "spec_hash": spec_hash,
            "generated_task_hash": generated_hash,
            "task_tree": _tree_digest(task_dir),
            "oracle_tree": oracle_tree,
            "compactness_reference": reference_record,
            "source_repo_id": snapshot.get("source_repo_id"),
            "source_snapshot_id": snapshot.get("source_snapshot_id"),
            "source_resolved_commit": snapshot.get("resolved_commit"),
            "source_tree_sha256": snapshot.get("source_tree_sha256"),
            "source_archive_sha256": snapshot.get("archive_sha256"),
            "source_archive_path": snapshot.get("archive_path"),
        }

    evaluator_paths = [
        ROOT / "harness" / "featureliftbench",
        ROOT / "harness" / "config",
        ROOT / "docker" / "Dockerfile.eval",
        ROOT / "pyproject.toml",
        ROOT / "scripts" / "materialize_full_sources.py",
        ROOT / "scripts" / "build_source_registry.py",
        ROOT / "scripts" / "audit_v2_main_readiness.py",
        ROOT / "scripts" / "revalidate_v2_oracles.py",
        ROOT / "scripts" / "build_v2_benchmark_freeze.py",
    ]
    evaluator_manifest = file_manifest(evaluator_paths, root=ROOT)
    vendor_manifest = file_manifest(
        [ROOT / "benchmark" / "vendor-wheels"],
        root=ROOT,
    )
    source_manifest = file_manifest(
        [
            registry_path,
            ROOT / "benchmark" / "sources" / "registry.schema.json",
            ROOT / "docs" / "FULL_REPOSITORY_SOURCE_POLICY.md",
            ROOT / "docs" / "BENCHMARK_DESIGN_PRINCIPLES.md",
            reference_registry_path,
        ],
        root=ROOT,
    )
    scoring_semantics = _validate_scoring_semantics()
    if not scoring_semantics["gate_pass"]:
        raise ValueError("v2 functional/compactness scoring probes failed")

    oracle_environment = oracle.get("environment") or {}
    docker_image = {
        "name": oracle_environment.get("name"),
        "id": oracle_environment.get("id"),
    }
    if not docker_image["id"]:
        docker_image = _docker_identity("featureliftbench-eval:latest")
    if not docker_image["id"]:
        raise ValueError("Docker evaluator image identity is unavailable")

    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "policy_id": POLICY_ID,
        "source_policy_id": SOURCE_POLICY_ID,
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "split": "python-main-150",
        "task_count": len(tasks),
        "gate_pass": True,
        "primary_metric": "functional_pass_at_1",
        "secondary_metrics": {
            "compactness": "independent_reference_relative_vector",
            "efficiency": "independent_trajectory_and_token_metrics",
        },
        "difficulty_policy": {
            "status": "empirical_labels_pending_first_v2_baseline",
            "legacy_core100_hard50_role": "historical_construction_strata_only",
            "admission_dependency": False,
        },
        "gates": {
            "task_validation": 150,
            "complete_public_contract": 150,
            "no_hint_workspace": 150,
            "full_repository_source": 150,
            "source_archives_verified": source_verification["verified_snapshots"],
            "oracle_runs_passed": 450,
            "oracle_tasks_stable": 150,
            "independent_submission": 150,
            "functional_primary_scoring": scoring_semantics["gate_pass"],
        },
        "oracle_revalidation": {
            "path": str(oracle_report_path.relative_to(ROOT)),
            "sha256": sha256_file(oracle_report_path),
            "schema_version": oracle.get("schema_version"),
            "backend": oracle_environment.get("backend"),
            "image": docker_image,
            "summary": oracle.get("summary"),
        },
        "readiness_evidence": {
            "path": str(readiness_report_path.relative_to(ROOT)),
            "sha256": sha256_file(readiness_report_path),
            "summary": readiness_summary,
        },
        "environment": {
            "eval_image": docker_image,
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "network_during_evaluation": "none",
            "agent_workspace_policy": "full_repository_no_hint",
            "tests_visible_to_agent": False,
        },
        "scoring_semantics": scoring_semantics,
        "evaluator_files": evaluator_manifest,
        "vendor_wheels": vendor_manifest,
        "source_policy_files": source_manifest,
        "source_registry_sha256": sha256_file(registry_path),
        "compactness_reference_registry": {
            "path": str(reference_registry_path.relative_to(ROOT)),
            "sha256": sha256_file(reference_registry_path),
            "registry_id": reference_registry.get("registry_id"),
            "task_count": reference_registry.get("task_count"),
        },
        "tasks": tasks,
    }
    payload["freeze_id"] = manifest_digest(payload)
    return payload


def verify_existing(payload: dict[str, Any]) -> None:
    if payload.get("policy_id") != POLICY_ID:
        raise ValueError("tracked freeze policy id is invalid")
    if payload.get("gate_pass") is not True or payload.get("task_count") != 150:
        raise ValueError("tracked freeze is not a passing Python-150 freeze")
    expected = manifest_digest(payload)
    if payload.get("freeze_id") != expected:
        raise ValueError("tracked freeze id is invalid")
    mismatches = []
    for field in ("evaluator_files", "vendor_wheels", "source_policy_files"):
        mismatches.extend(
            verify_file_manifest(payload.get(field, {}), root=ROOT)
        )
    if mismatches:
        raise ValueError(f"frozen files have drifted: {mismatches[:3]}")
    if sha256_file(ROOT / "benchmark" / "sources" / "registry.json") != payload.get(
        "source_registry_sha256"
    ):
        raise ValueError("canonical source registry has drifted")
    compactness_registry = payload.get("compactness_reference_registry")
    if not isinstance(compactness_registry, dict):
        raise ValueError("compactness reference registry is absent from freeze")
    compactness_path = ROOT / str(compactness_registry.get("path") or "")
    if (
        not compactness_path.is_file()
        or sha256_file(compactness_path) != compactness_registry.get("sha256")
    ):
        raise ValueError("compactness reference registry has drifted")
    task_records = payload.get("tasks")
    if not isinstance(task_records, dict) or len(task_records) != 150:
        raise ValueError("tracked task records are incomplete")
    for task_id, record in sorted(task_records.items()):
        if not isinstance(record, dict):
            raise ValueError(f"{task_id}: invalid freeze record")
        task_dir = ROOT / "benchmark" / "tasks" / task_id
        oracle_dir = ROOT / "benchmark" / "submissions" / task_id / "oracle"
        if _tree_digest(task_dir) != record.get("task_tree"):
            raise ValueError(f"{task_id}: task tree has drifted")
        if _tree_digest(oracle_dir) != record.get("oracle_tree"):
            raise ValueError(f"{task_id}: Oracle tree has drifted")


def main() -> int:
    args = _parse_args()
    output = args.output.resolve()
    if args.check:
        payload = _load(output)
        verify_existing(payload)
        print(f"Verified v2 benchmark freeze: {payload['freeze_id']}")
        return 0
    payload = build_payload(
        args.oracle_report.resolve(),
        args.readiness_report.resolve(),
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    immutable = output.parent / "freezes" / f"{payload['freeze_id']}.json"
    immutable.parent.mkdir(parents=True, exist_ok=True)
    if immutable.exists() and _load(immutable) != payload:
        raise ValueError(f"immutable freeze collision: {immutable}")
    shutil.copy2(output, immutable)
    print(f"Wrote passing v2 benchmark freeze: {payload['freeze_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
