#!/usr/bin/env python3
"""Build or verify the hardened External-150 benchmark freeze."""

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
from featureliftbench.scoring import functional_gate, score_submission
from featureliftbench.source_archive import load_source_registry, source_indexes
from featureliftbench.task_spec import compute_generated_task_hash, compute_spec_hash
from featureliftbench.validate import validate_task


POLICY_ID = "featureliftbench.full_repository_no_hint_main.v3"
SOURCE_POLICY_ID = "featureliftbench.full_repository_source.v2"
SCHEMA_VERSION = "featureliftbench.benchmark_freeze.v3"
DEFAULT_ORACLE = ROOT / "reports" / "audits" / "v3_oracle_revalidation" / "summary.json"
DEFAULT_READINESS = ROOT / "reports" / "audits" / "v3_main_readiness.json"
DEFAULT_CANARIES = ROOT / "reports" / "audits" / "v3_adversarial_canaries.json"
DEFAULT_OUTPUT = (
    ROOT
    / "artifacts"
    / "research_analysis"
    / "v3"
    / "current_benchmark_freeze.json"
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oracle-report", type=Path, default=DEFAULT_ORACLE)
    parser.add_argument("--readiness-report", type=Path, default=DEFAULT_READINESS)
    parser.add_argument("--canary-report", type=Path, default=DEFAULT_CANARIES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
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
    return {"name": image, "id": completed.stdout.strip()}


def _scoring_semantics() -> dict[str, Any]:
    cases = {
        "all_pass": functional_gate(
            build_pass=True,
            public_tests_pass=True,
            hidden_tests_pass=True,
            isolation_pass=True,
        ),
        "build_fail": functional_gate(
            build_pass=False,
            public_tests_pass=True,
            hidden_tests_pass=True,
            isolation_pass=True,
        ),
        "public_fail": functional_gate(
            build_pass=True,
            public_tests_pass=False,
            hidden_tests_pass=True,
            isolation_pass=True,
        ),
        "hidden_fail": functional_gate(
            build_pass=True,
            public_tests_pass=True,
            hidden_tests_pass=False,
            isolation_pass=True,
        ),
        "isolation_fail": functional_gate(
            build_pass=True,
            public_tests_pass=True,
            hidden_tests_pass=True,
            isolation_pass=False,
        ),
    }
    compact = score_submission(
        metrics={"loc": 100, "reference_loc": 100},
        metadata={},
        functional_gate_score=1.0,
    )
    copy_all = score_submission(
        metrics={"loc": 10_000, "reference_loc": 100},
        metadata={},
        functional_gate_score=1.0,
    )
    gate_pass = (
        cases["all_pass"] == 1.0
        and all(cases[key] == 0.0 for key in cases if key != "all_pass")
        and compact["final_score"] == compact["functional_gate"] == 1.0
        and copy_all["final_score"] == copy_all["functional_gate"] == 1.0
        and copy_all["compactness_score"] < compact["compactness_score"]
    )
    return {
        "gate_pass": gate_pass,
        "functional_gate_cases": cases,
        "reference_sized_probe": compact,
        "copy_all_probe": copy_all,
    }


def _verify_source_archives(registry: dict[str, Any]) -> dict[str, Any]:
    failures: list[dict[str, str]] = []
    snapshots = [
        row for row in registry.get("snapshots", []) if isinstance(row, dict)
    ]
    verified = 0
    for snapshot in snapshots:
        snapshot_id = str(snapshot.get("source_snapshot_id") or "")
        archive = ROOT / str(snapshot.get("archive_path") or "")
        if (
            snapshot.get("status") != "ready"
            or snapshot.get("current_snapshot_scope") != "full_tracked_tree"
        ):
            failures.append({"snapshot_id": snapshot_id, "reason": "not ready/full"})
            continue
        if not archive.is_file():
            failures.append({"snapshot_id": snapshot_id, "reason": "archive missing"})
            continue
        actual = sha256_file(archive)
        if actual != snapshot.get("archive_sha256"):
            failures.append(
                {"snapshot_id": snapshot_id, "reason": "archive digest mismatch"}
            )
            continue
        verified += 1
    return {
        "gate_pass": verified == len(snapshots) and not failures,
        "snapshot_count": len(snapshots),
        "verified_snapshots": verified,
        "failures": failures,
    }


def _require_evidence(
    payload: dict[str, Any],
    *,
    schema: str,
    label: str,
) -> None:
    if (
        payload.get("schema_version") != schema
        or payload.get("policy_id") != POLICY_ID
        or payload.get("gate_pass") is not True
    ):
        raise ValueError(f"{label} is not passing hardened v3 evidence")


def build_payload(
    oracle_path: Path,
    readiness_path: Path,
    canary_path: Path,
) -> dict[str, Any]:
    oracle = _load(oracle_path)
    readiness = _load(readiness_path)
    canaries = _load(canary_path)
    _require_evidence(
        oracle,
        schema="featureliftbench.v3_oracle_revalidation.v1",
        label="Oracle report",
    )
    _require_evidence(
        readiness,
        schema="featureliftbench.v3_main_readiness.v1",
        label="readiness report",
    )
    _require_evidence(
        canaries,
        schema="featureliftbench.v3_adversarial_canaries.v1",
        label="adversarial canary report",
    )
    oracle_summary = oracle.get("summary") or {}
    if (
        oracle_summary.get("task_count") != 150
        or oracle_summary.get("repetitions", 0) < 3
        or oracle_summary.get("passed_runs") != 450
        or oracle_summary.get("stable_tasks") != 150
        or oracle.get("failed_task_ids")
        or oracle.get("unstable_task_ids")
    ):
        raise ValueError("Oracle evidence does not satisfy 150 x 3 = 450/450")
    readiness_summary = readiness.get("summary") or {}
    required_readiness = (
        "task_pass_count",
        "validation_pass",
        "source_pass",
        "workspace_pass",
        "contract_pass",
        "capsule_pass",
        "compactness_pass",
        "split_pass",
    )
    if any(readiness_summary.get(key) != 150 for key in required_readiness):
        raise ValueError("readiness report does not have all per-task gates at 150")

    registry_path = ROOT / "benchmark" / "sources" / "registry.json"
    registry = load_source_registry(registry_path)
    registry_summary = registry.get("summary") or {}
    if (
        registry.get("policy_id") != SOURCE_POLICY_ID
        or registry_summary.get("task_count") != 150
        or registry_summary.get("external_repository_count") != 126
        or registry_summary.get("curated_repository_count") != 0
        or registry_summary.get("snapshot_count") != 132
        or registry_summary.get("ready_snapshot_count") != 132
        or registry_summary.get("pending_snapshot_count") != 0
    ):
        raise ValueError("External-150 source registry is incomplete")
    source_verification = _verify_source_archives(registry)
    if not source_verification["gate_pass"]:
        raise ValueError(
            f"source archives failed verification: {source_verification['failures'][:3]}"
        )
    _, task_snapshots = source_indexes(registry)

    task_dirs = sorted(
        path
        for path in (ROOT / "benchmark" / "tasks").iterdir()
        if path.is_dir() and (path / "metadata.json").is_file()
    )
    curated_dirs = sorted(
        path
        for path in (ROOT / "benchmark" / "curated" / "tasks").iterdir()
        if path.is_dir() and (path / "metadata.json").is_file()
    )
    if len(task_dirs) != 150 or len(curated_dirs) != 7:
        raise ValueError("expected External Main=150 and Curated=7")

    reference_path = ROOT / "benchmark" / "references" / "compactness.json"
    reference_registry = _load(reference_path)
    reference_tasks = reference_registry.get("tasks")
    if (
        reference_registry.get("task_count") != 150
        or not isinstance(reference_tasks, dict)
        or set(reference_tasks) != {path.name for path in task_dirs}
    ):
        raise ValueError("compactness reference registry is incomplete or contaminated")

    tasks: dict[str, dict[str, Any]] = {}
    for task_dir in task_dirs:
        task_id = task_dir.name
        metadata = _load(task_dir / "metadata.json")
        validation = validate_task(task_dir)
        if not validation.valid:
            raise ValueError(f"{task_id}: {'; '.join(validation.errors)}")
        public_spec = metadata.get("public_spec")
        if not isinstance(public_spec, dict):
            raise ValueError(f"{task_id}: public_spec missing")
        spec_hash = compute_spec_hash(public_spec)
        generated_hash = compute_generated_task_hash(
            (task_dir / "TASK.md").read_text(encoding="utf-8")
        )
        if metadata.get("spec_hash") != spec_hash:
            raise ValueError(f"{task_id}: spec hash mismatch")
        if metadata.get("generated_task_hash") != generated_hash:
            raise ValueError(f"{task_id}: generated TASK hash mismatch")
        snapshot = task_snapshots.get(task_id)
        if (
            not isinstance(snapshot, dict)
            or snapshot.get("status") != "ready"
            or snapshot.get("current_snapshot_scope") != "full_tracked_tree"
        ):
            raise ValueError(f"{task_id}: full source snapshot unavailable")
        oracle_dir = ROOT / "benchmark" / "submissions" / task_id / "oracle"
        if not oracle_dir.is_dir():
            raise ValueError(f"{task_id}: reference submission missing")
        oracle_tree = _tree_digest(oracle_dir)
        reference = reference_tasks.get(task_id)
        if (
            not isinstance(reference, dict)
            or reference.get("reference_tree_sha256") != oracle_tree["sha256"]
        ):
            raise ValueError(f"{task_id}: reference registry drift")
        tasks[task_id] = {
            "task_revision": metadata.get("task_revision"),
            "spec_hash": spec_hash,
            "generated_task_hash": generated_hash,
            "task_tree": _tree_digest(task_dir),
            "reference_tree": oracle_tree,
            "compactness_reference": reference,
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
        ROOT / "harness" / "scripts" / "run_python150_paper.sh",
        ROOT / "docker" / "Dockerfile.eval",
        ROOT / "pyproject.toml",
        ROOT / "scripts" / "materialize_full_sources.py",
        ROOT / "scripts" / "build_source_registry.py",
        ROOT / "scripts" / "build_pruned_source_registry.py",
        ROOT / "scripts" / "audit_v3_main_readiness.py",
        ROOT / "scripts" / "revalidate_v3_oracles.py",
        ROOT / "scripts" / "run_v3_adversarial_canaries.py",
        ROOT / "scripts" / "build_v3_benchmark_freeze.py",
    ]
    evaluator_manifest = file_manifest(evaluator_paths, root=ROOT)
    vendor_manifest = file_manifest(
        [ROOT / "benchmark" / "vendor-wheels"],
        root=ROOT,
    )
    policy_paths = [
        registry_path,
        ROOT / "benchmark" / "sources" / "registry.schema.json",
        ROOT / "benchmark" / "sources" / "pruned_registry.json",
        ROOT / "benchmark" / "selection" / "external150_replacement_20260727.json",
        ROOT / "docs" / "FULL_REPOSITORY_SOURCE_POLICY.md",
        ROOT / "docs" / "BENCHMARK_DESIGN_PRINCIPLES.md",
        reference_path,
    ]
    policy_manifest = file_manifest(policy_paths, root=ROOT)
    scoring = _scoring_semantics()
    if not scoring["gate_pass"]:
        raise ValueError("functional/compactness separation probe failed")

    oracle_environment = oracle.get("environment") or {}
    image = {
        "name": oracle_environment.get("name"),
        "id": oracle_environment.get("id"),
    }
    if not image["id"]:
        image = _docker_identity("featureliftbench-eval:latest")
    if not image["id"]:
        raise ValueError("Docker evaluator image identity unavailable")

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
        "secondary_metrics": {
            "compactness": "reference_relative_static_metrics_only",
            "efficiency": "trajectory_steps_tokens_latency_cost",
        },
        "historical_results_policy": {
            "label": "mixed_snapshot_v1",
            "headline_eligible": False,
        },
        "agent_condition": {
            "source_context": "full_repository",
            "source_hints_visible": False,
            "benchmark_tests_visible": False,
            "prompt_style": "standard",
            "extra_agent_passes": 0,
            "max_task_attempts": 1,
        },
        "evaluation_condition": {
            "functional_stage": "source_free_docker_capsule",
            "metrics_stage": "trusted_static_read_only_no_submission_execution",
            "network": "none",
            "read_only_rootfs": True,
            "cap_drop": "ALL",
            "hidden_definition": "not visible to Agent before submission",
        },
        "gates": {
            "task_validation": 150,
            "complete_contract_mapping": 150,
            "full_repository_no_hint_test_blind_workspace": 150,
            "source_free_functional_capsule": 150,
            "external_full_source": 150,
            "source_archives_verified": source_verification["verified_snapshots"],
            "reference_relative_compactness": 150,
            "oracle_runs_passed": 450,
            "oracle_tasks_stable": 150,
            "adversarial_canaries": len(canaries.get("cases") or {}),
            "functional_primary_scoring": scoring["gate_pass"],
        },
        "oracle_revalidation": {
            "path": str(oracle_path.relative_to(ROOT)),
            "sha256": sha256_file(oracle_path),
            "schema_version": oracle.get("schema_version"),
            "image": image,
            "summary": oracle_summary,
        },
        "readiness_evidence": {
            "path": str(readiness_path.relative_to(ROOT)),
            "sha256": sha256_file(readiness_path),
            "schema_version": readiness.get("schema_version"),
            "summary": readiness_summary,
        },
        "adversarial_evidence": {
            "path": str(canary_path.relative_to(ROOT)),
            "sha256": sha256_file(canary_path),
            "schema_version": canaries.get("schema_version"),
            "compactness_separation_pass": canaries.get(
                "compactness_separation_pass"
            ),
        },
        "environment": {
            "eval_image": image,
            "python_version": platform.python_version(),
            "platform": platform.platform(),
        },
        "scoring_semantics": scoring,
        "evaluator_files": evaluator_manifest,
        "vendor_wheels": vendor_manifest,
        "policy_files": policy_manifest,
        "source_registry_sha256": sha256_file(registry_path),
        "compactness_reference_registry": {
            "path": str(reference_path.relative_to(ROOT)),
            "sha256": sha256_file(reference_path),
            "registry_id": reference_registry.get("registry_id"),
            "task_count": reference_registry.get("task_count"),
        },
        "tasks": tasks,
    }
    payload["freeze_id"] = manifest_digest(payload)
    return payload


def verify_existing(payload: dict[str, Any]) -> None:
    if (
        payload.get("policy_id") != POLICY_ID
        or payload.get("source_policy_id") != SOURCE_POLICY_ID
        or payload.get("gate_pass") is not True
        or payload.get("task_count") != 150
        or payload.get("curated_task_count") != 7
    ):
        raise ValueError("tracked freeze is not a passing v3 External-150 freeze")
    if payload.get("freeze_id") != manifest_digest(payload):
        raise ValueError("tracked freeze id is invalid")
    mismatches: list[dict[str, str]] = []
    for field in ("evaluator_files", "vendor_wheels", "policy_files"):
        manifest = payload.get(field)
        if not isinstance(manifest, dict):
            raise ValueError(f"freeze manifest missing: {field}")
        mismatches.extend(verify_file_manifest(manifest, root=ROOT))
    if mismatches:
        raise ValueError(f"frozen files drifted: {mismatches[:3]}")
    if sha256_file(ROOT / "benchmark" / "sources" / "registry.json") != payload.get(
        "source_registry_sha256"
    ):
        raise ValueError("source registry drifted")
    compactness = payload.get("compactness_reference_registry")
    if not isinstance(compactness, dict):
        raise ValueError("compactness registry freeze missing")
    compactness_path = ROOT / str(compactness.get("path") or "")
    if (
        not compactness_path.is_file()
        or sha256_file(compactness_path) != compactness.get("sha256")
    ):
        raise ValueError("compactness registry drifted")
    records = payload.get("tasks")
    if not isinstance(records, dict) or len(records) != 150:
        raise ValueError("task freeze records incomplete")
    for task_id, record in sorted(records.items()):
        if not isinstance(record, dict):
            raise ValueError(f"{task_id}: invalid freeze record")
        task_dir = ROOT / "benchmark" / "tasks" / task_id
        reference_dir = ROOT / "benchmark" / "submissions" / task_id / "oracle"
        if _tree_digest(task_dir) != record.get("task_tree"):
            raise ValueError(f"{task_id}: task tree drifted")
        if _tree_digest(reference_dir) != record.get("reference_tree"):
            raise ValueError(f"{task_id}: reference tree drifted")
    for evidence_key in (
        "oracle_revalidation",
        "readiness_evidence",
        "adversarial_evidence",
    ):
        evidence = payload.get(evidence_key)
        if not isinstance(evidence, dict):
            raise ValueError(f"{evidence_key} missing")
        path = ROOT / str(evidence.get("path") or "")
        if not path.is_file() or sha256_file(path) != evidence.get("sha256"):
            raise ValueError(f"{evidence_key} drifted")


def main() -> int:
    args = _parse_args()
    output = args.output.resolve()
    if args.check:
        payload = _load(output)
        verify_existing(payload)
        print(f"Verified v3 benchmark freeze: {payload['freeze_id']}")
        return 0
    payload = build_payload(
        args.oracle_report.resolve(),
        args.readiness_report.resolve(),
        args.canary_report.resolve(),
    )
    immutable = output.parent / "freezes" / f"{payload['freeze_id']}.json"
    immutable.parent.mkdir(parents=True, exist_ok=True)
    if immutable.exists():
        existing = _load(immutable)
        if (
            existing.get("freeze_id") != payload["freeze_id"]
            or manifest_digest(existing) != payload["freeze_id"]
        ):
            raise ValueError(f"immutable freeze collision: {immutable}")
        verify_existing(existing)
        payload = existing
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    if not immutable.exists():
        shutil.copy2(output, immutable)
    print(f"Wrote passing v3 benchmark freeze: {payload['freeze_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
