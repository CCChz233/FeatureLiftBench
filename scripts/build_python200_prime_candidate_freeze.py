#!/usr/bin/env python3
"""Build or verify the content-addressed Python-200-prime freeze candidate.

This manifest intentionally remains a candidate until the pinned evaluator image
and the unified 200-task Oracle revalidation are attached by the final-freeze
builder.  It freezes everything that can be established before those runtime
gates: task packages, references, source snapshots, evaluator code, policy
files, vendored wheels, and hidden-contract remediation evidence.
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
    verify_file_manifest,
)
from featureliftbench.source_archive import (  # noqa: E402
    load_source_registry,
    source_indexes,
)
from featureliftbench.task_spec import (  # noqa: E402
    compute_generated_task_hash,
    compute_spec_hash,
)
from featureliftbench.validate import validate_task  # noqa: E402


SCHEMA_VERSION = "featureliftbench.python200_prime_candidate_freeze.v1"
POLICY_ID = "featureliftbench.full_repository_no_hint_main.v3"
SOURCE_POLICY_ID = "featureliftbench.full_repository_source.v2"
DEFAULT_SUITE = ROOT / "benchmark" / "selection" / "python200_hard_suite.json"
DEFAULT_REGISTRY = ROOT / "benchmark" / "sources" / "python200_hard_registry.json"
DEFAULT_HIDDEN_LEDGER = (
    ROOT
    / "artifacts"
    / "research_analysis"
    / "hidden_provenance"
    / "python200_prime_candidate_rejudgement_20260831.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "artifacts"
    / "research_analysis"
    / "python200_prime"
    / "current_candidate_freeze.json"
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", type=Path, default=DEFAULT_SUITE)
    parser.add_argument("--source-registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--hidden-ledger", type=Path, default=DEFAULT_HIDDEN_LEDGER)
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


def _tree_digest(path: Path) -> dict[str, Any]:
    resolved = path.resolve()
    files = file_manifest([resolved], root=resolved)
    return {"sha256": manifest_digest({"files": files}), "file_count": len(files)}


def _candidate_digest(payload: dict[str, Any]) -> str:
    normalized = dict(payload)
    normalized.pop("candidate_id", None)
    return manifest_digest(normalized)


def _reference_dir(task_id: str) -> tuple[Path, str]:
    baseline = ROOT / "benchmark" / "submissions" / task_id / "oracle"
    if baseline.is_dir():
        return baseline, "python150_oracle"
    hard50 = ROOT / "benchmark" / "hard50_pilot" / task_id / "reference_solution"
    if hard50.is_dir():
        return hard50, "hard50_reference_solution"
    raise ValueError(f"{task_id}: reference solution missing")


def _verify_sources(registry: dict[str, Any]) -> dict[str, Any]:
    failures: list[dict[str, str]] = []
    verified = 0
    snapshots = [row for row in registry.get("snapshots", []) if isinstance(row, dict)]
    for snapshot in snapshots:
        snapshot_id = str(snapshot.get("source_snapshot_id") or "")
        archive = ROOT / str(snapshot.get("archive_path") or "")
        if snapshot.get("status") != "ready":
            failures.append({"snapshot_id": snapshot_id, "reason": "not ready"})
        elif snapshot.get("current_snapshot_scope") != "full_tracked_tree":
            failures.append({"snapshot_id": snapshot_id, "reason": "not full tracked tree"})
        elif not archive.is_file():
            failures.append({"snapshot_id": snapshot_id, "reason": "archive missing"})
        elif sha256_file(archive) != snapshot.get("archive_sha256"):
            failures.append({"snapshot_id": snapshot_id, "reason": "archive digest mismatch"})
        else:
            verified += 1
    return {
        "gate_pass": not failures and verified == len(snapshots),
        "snapshot_count": len(snapshots),
        "verified_snapshot_count": verified,
        "failures": failures,
    }


def build_payload(suite_path: Path, registry_path: Path, hidden_path: Path) -> dict[str, Any]:
    suite = _load(suite_path)
    registry = load_source_registry(registry_path)
    hidden = _load(hidden_path)
    task_ids = suite.get("task_ids")
    if not isinstance(task_ids, list) or len(task_ids) != 200 or len(set(task_ids)) != 200:
        raise ValueError("suite must contain exactly 200 unique task ids")
    task_root = ROOT / str(suite.get("task_root") or "")
    materialized_ids = sorted(
        path.name
        for path in task_root.iterdir()
        if path.is_dir() and (path / "metadata.json").is_file()
    )
    if sorted(task_ids) != materialized_ids:
        raise ValueError("suite membership differs from materialized Python-200-prime root")
    if registry.get("policy_id") != SOURCE_POLICY_ID:
        raise ValueError("unexpected source policy")
    if (registry.get("summary") or {}).get("task_count") != 200:
        raise ValueError("source registry does not cover 200 tasks")
    source_verification = _verify_sources(registry)
    if not source_verification["gate_pass"]:
        raise ValueError(f"source verification failed: {source_verification['failures'][:3]}")
    _, task_snapshots = source_indexes(registry)
    if set(task_snapshots) != set(task_ids):
        missing = sorted(set(task_ids) - set(task_snapshots))
        extra = sorted(set(task_snapshots) - set(task_ids))
        raise ValueError(f"source mapping mismatch: missing={missing[:3]} extra={extra[:3]}")
    hidden_summary = hidden.get("summary") or {}
    if hidden_summary.get("unresolved_in_current_candidate") != 0:
        raise ValueError("hidden-contract remediation ledger is unresolved")

    baseline_ids = {
        path.name
        for path in (ROOT / "benchmark" / "tasks").iterdir()
        if path.is_dir() and (path / "metadata.json").is_file()
    }
    if len(baseline_ids) != 150:
        raise ValueError(f"expected 150 baseline tasks, found {len(baseline_ids)}")

    tasks: dict[str, dict[str, Any]] = {}
    reference_counts = {"python150_oracle": 0, "hard50_reference_solution": 0}
    for task_id in sorted(task_ids):
        task_dir = task_root / task_id
        validation = validate_task(task_dir)
        if not validation.valid:
            raise ValueError(f"{task_id}: {'; '.join(validation.errors)}")
        metadata = _load(task_dir / "metadata.json")
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
        snapshot = task_snapshots[task_id]
        reference_dir, reference_kind = _reference_dir(task_id)
        reference_counts[reference_kind] += 1
        tasks[task_id] = {
            "stratum": "python150" if task_id in baseline_ids else "hard50",
            "task_revision": metadata.get("task_revision"),
            "spec_hash": spec_hash,
            "generated_task_hash": generated_hash,
            "task_tree": _tree_digest(task_dir),
            "reference_kind": reference_kind,
            "reference_tree": _tree_digest(reference_dir),
            "source_repo_id": snapshot.get("source_repo_id"),
            "source_snapshot_id": snapshot.get("source_snapshot_id"),
            "source_resolved_commit": snapshot.get("resolved_commit"),
            "source_tree_sha256": snapshot.get("source_tree_sha256"),
            "source_archive_sha256": snapshot.get("archive_sha256"),
            "source_archive_path": snapshot.get("archive_path"),
        }
    if reference_counts != {"python150_oracle": 150, "hard50_reference_solution": 50}:
        raise ValueError(f"unexpected reference composition: {reference_counts}")

    evaluator_paths = [
        ROOT / "harness" / "featureliftbench",
        ROOT / "harness" / "config",
        ROOT / "docker" / "Dockerfile.agent",
        ROOT / "docker" / "Dockerfile.eval",
        ROOT / "docker" / "build_agent_image.sh",
        ROOT / "docker" / "build_eval_image.sh",
        ROOT / "pyproject.toml",
        ROOT / "scripts" / "build_python200_prime_candidate_freeze.py",
        ROOT / "scripts" / "build_python200_prime_compactness_registry.py",
        ROOT / "scripts" / "revalidate_python200_prime_oracles.py",
    ]
    policy_paths = [
        suite_path,
        registry_path,
        ROOT / "benchmark" / "sources" / "registry.schema.json",
        ROOT / "benchmark" / "selection" / "hard50_expansion_20260827.json",
        ROOT / "benchmark" / "selection" / "scripts" / "materialize_python200_hard_release.py",
        ROOT / "benchmark" / "references" / "python200_prime_compactness.json",
        ROOT / "docs" / "FULL_REPOSITORY_SOURCE_POLICY.md",
        ROOT / "docs" / "BENCHMARK_DESIGN_PRINCIPLES.md",
        ROOT / "docs" / "HIDDEN_CONTRACT_PROVENANCE.md",
        hidden_path,
    ]
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "policy_id": POLICY_ID,
        "source_policy_id": SOURCE_POLICY_ID,
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "status": "candidate",
        "gate_pass": False,
        "promotion_blockers": [
            "pinned_linux_amd64_agent_and_evaluator_images",
            "unified_python200_prime_oracle_revalidation",
        ],
        "suite_id": suite.get("suite_id"),
        "task_count": 200,
        "strata": {"python150": 150, "hard50": 50},
        "task_set_sha256": suite.get("task_set_sha256"),
        "primary_metric": "functional_pass_at_1",
        "functional_definition": "Build AND Public AND Hidden AND Isolation",
        "agent_condition": {
            "source_context": "full_repository",
            "source_hints_visible": False,
            "benchmark_tests_visible": False,
            "max_task_attempts": 1,
        },
        "evaluation_condition": {
            "network": "none",
            "read_only_rootfs": True,
            "cap_drop": "ALL",
            "hidden_definition": "not visible to Agent before submission",
        },
        "pre_runtime_gates": {
            "task_validation": 200,
            "source_mapping": 200,
            "source_archives_verified": source_verification["verified_snapshot_count"],
            "reference_solutions": reference_counts,
            "hidden_contract_candidate_unresolved": 0,
        },
        "source_verification": source_verification,
        "source_registry_sha256": sha256_file(registry_path),
        "suite_manifest_sha256": sha256_file(suite_path),
        "hidden_contract_ledger": {
            "path": _relative(hidden_path),
            "sha256": sha256_file(hidden_path),
            "review_status": hidden.get("review_status"),
            "summary": hidden_summary,
        },
        "evaluator_files": file_manifest(evaluator_paths, root=ROOT),
        "policy_files": file_manifest(policy_paths, root=ROOT),
        "vendor_wheels": file_manifest([ROOT / "benchmark" / "vendor-wheels"], root=ROOT),
        "tasks": tasks,
    }
    payload["candidate_id"] = _candidate_digest(payload)
    return payload


def verify_existing(payload: dict[str, Any]) -> None:
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unexpected candidate schema")
    if payload.get("status") != "candidate" or payload.get("gate_pass") is not False:
        raise ValueError("candidate must not claim final gate pass")
    if payload.get("task_count") != 200 or len(payload.get("tasks") or {}) != 200:
        raise ValueError("candidate does not freeze 200 tasks")
    if payload.get("candidate_id") != _candidate_digest(payload):
        raise ValueError("candidate id is invalid")
    mismatches: list[dict[str, str]] = []
    for field in ("evaluator_files", "policy_files", "vendor_wheels"):
        manifest = payload.get(field)
        if not isinstance(manifest, dict):
            raise ValueError(f"manifest missing: {field}")
        mismatches.extend(verify_file_manifest(manifest, root=ROOT))
    if mismatches:
        raise ValueError(f"frozen files drifted: {mismatches[:3]}")
    task_root = ROOT / "benchmark" / "python200_hard_tasks"
    for task_id, record in sorted((payload.get("tasks") or {}).items()):
        if _tree_digest(task_root / task_id) != record.get("task_tree"):
            raise ValueError(f"{task_id}: task tree drifted")
        reference_dir, _ = _reference_dir(task_id)
        if _tree_digest(reference_dir) != record.get("reference_tree"):
            raise ValueError(f"{task_id}: reference tree drifted")


def main() -> int:
    args = _parse_args()
    output = args.output.resolve()
    if args.check:
        payload = _load(output)
        verify_existing(payload)
        print(f"Verified Python-200-prime candidate: {payload['candidate_id']}")
        return 0
    payload = build_payload(
        args.suite.resolve(), args.source_registry.resolve(), args.hidden_ledger.resolve()
    )
    immutable = output.parent / "candidates" / f"{payload['candidate_id']}.json"
    immutable.parent.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if immutable.exists():
        existing = _load(immutable)
        if existing.get("candidate_id") != payload["candidate_id"]:
            raise ValueError(f"immutable candidate collision: {immutable}")
    else:
        shutil.copy2(output, immutable)
    verify_existing(payload)
    print(f"Wrote Python-200-prime candidate: {payload['candidate_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
