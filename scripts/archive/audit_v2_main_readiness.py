#!/usr/bin/env python3
"""Audit all Python tasks against the FeatureLiftBench v2 core principles."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
import tempfile
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "harness"
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))

from featureliftbench.ablation import AblationOptions
from featureliftbench.agent_runner import (
    audit_no_hint_workspace,
    prepare_agent_workspace,
)
from featureliftbench.metadata import load_metadata
from featureliftbench.task_spec import SPEC_STATUS_COMPLIANT
from featureliftbench.validate import validate_task


POLICY_ID = "featureliftbench.full_repository_no_hint_main.v2"
SCHEMA_VERSION = "featureliftbench.v2_main_readiness.v1"
DEFAULT_TASKS_ROOT = ROOT / "benchmark" / "tasks"
DEFAULT_SOURCE_REGISTRY = ROOT / "benchmark" / "sources" / "registry.json"
DEFAULT_SPEC_FREEZE = (
    ROOT / "artifacts" / "research_analysis" / "v1_1" / "current_spec_freeze.json"
)
DEFAULT_V2_FREEZE = (
    ROOT / "artifacts" / "research_analysis" / "v2" / "current_benchmark_freeze.json"
)
DEFAULT_JSON_OUT = ROOT / "reports" / "audits" / "v2_main_readiness.json"
DEFAULT_CSV_OUT = ROOT / "reports" / "audits" / "v2_main_readiness.csv"
DEFAULT_MARKDOWN_OUT = ROOT / "reports" / "audits" / "v2_main_readiness.md"

PRIVATE_HINT_KEYS = frozenset(
    {
        "source_entrypoints",
        "source_hints",
        "entrypoints",
        "repo_files",
        "source_files",
        "target_files",
        "implementation_hints",
    }
)
EVALUATOR_ONLY_PATHS = (
    "public_tests",
    "hidden_tests",
    "evaluation",
    "reference_solution",
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks-root", type=Path, default=DEFAULT_TASKS_ROOT)
    parser.add_argument(
        "--source-registry",
        type=Path,
        default=DEFAULT_SOURCE_REGISTRY,
    )
    parser.add_argument("--spec-freeze", type=Path, default=DEFAULT_SPEC_FREEZE)
    parser.add_argument("--v2-freeze", type=Path, default=DEFAULT_V2_FREEZE)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--csv-out", type=Path, default=DEFAULT_CSV_OUT)
    parser.add_argument(
        "--markdown-out",
        type=Path,
        default=DEFAULT_MARKDOWN_OUT,
    )
    parser.add_argument(
        "--skip-workspace-materialization",
        action="store_true",
        help=(
            "audit rendered/redacted data in memory without constructing every "
            "Agent workspace; intended only for fast unit tests"
        ),
    )
    parser.add_argument(
        "--strict-v2",
        action="store_true",
        help="exit 1 unless every task is ready for Full-Repository / No-Hint Main",
    )
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _task_dirs(tasks_root: Path) -> list[Path]:
    return sorted(
        path
        for path in tasks_root.iterdir()
        if path.is_dir() and (path / "metadata.json").is_file()
    )


def _registry_indexes(
    registry: dict[str, Any],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    repositories = {
        str(item["source_repo_id"]): item
        for item in registry.get("repositories", [])
        if isinstance(item, dict) and item.get("source_repo_id")
    }
    task_snapshots: dict[str, dict[str, Any]] = {}
    duplicate_tasks: set[str] = set()
    for snapshot in registry.get("snapshots", []):
        if not isinstance(snapshot, dict):
            continue
        for raw_task_id in snapshot.get("task_ids", []):
            task_id = str(raw_task_id)
            if task_id in task_snapshots:
                duplicate_tasks.add(task_id)
            task_snapshots[task_id] = snapshot
    if duplicate_tasks:
        raise ValueError(
            "tasks map to multiple source snapshots: "
            + ", ".join(sorted(duplicate_tasks))
        )
    return repositories, task_snapshots


def _walk_hint_keys(value: Any, path: str = "") -> list[str]:
    leaks: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            child = f"{path}.{key}" if path else str(key)
            if key in PRIVATE_HINT_KEYS:
                leaks.append(child)
            leaks.extend(_walk_hint_keys(item, child))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            leaks.extend(_walk_hint_keys(item, f"{path}[{index}]"))
    return leaks


def _private_entrypoints(metadata: dict[str, Any]) -> list[str]:
    values: set[str] = set()
    for container_name in ("public_spec", "evaluation_spec", "feature"):
        container = metadata.get(container_name)
        if not isinstance(container, dict):
            continue
        for key in ("source_entrypoints", "source_hints"):
            raw = container.get(key)
            if isinstance(raw, list):
                values.update(
                    str(item).strip()
                    for item in raw
                    if isinstance(item, str) and item.strip()
                )
    raw = metadata.get("source_hints")
    if isinstance(raw, list):
        values.update(
            str(item).strip()
            for item in raw
            if isinstance(item, str) and item.strip()
        )
    return sorted(values)


def _target_api_paths(metadata: dict[str, Any]) -> set[str]:
    paths: set[str] = set()

    def walk(entries: Any) -> None:
        if not isinstance(entries, list):
            return
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            path = entry.get("path")
            if isinstance(path, str) and path:
                paths.add(path)
                paths.add(path.removeprefix("featurelifted."))
            walk(entry.get("members"))

    public_spec = metadata.get("public_spec")
    if isinstance(public_spec, dict):
        walk(public_spec.get("required_api"))
        walk(public_spec.get("optional_api"))
    return paths


def _entrypoint_visible_outside_target_api(
    text: str,
    entrypoint: str,
    target_api_paths: set[str],
) -> bool:
    if not entrypoint:
        return False

    # A public target API is part of the functional contract, not a source
    # locator hint. Some tasks intentionally preserve an upstream namespace
    # beneath ``featurelifted``.
    if entrypoint in target_api_paths:
        return False
    scrubbed = text.replace(f"featurelifted.{entrypoint}", "")
    return entrypoint in scrubbed


def _audit_workspace(
    task_dir: Path,
    metadata: dict[str, Any],
    scratch_root: Path,
) -> dict[str, Any]:
    workspace = scratch_root / task_dir.name
    task_file = prepare_agent_workspace(
        task_dir,
        workspace,
        metadata,
        ablation=AblationOptions(),
    )
    leaks = audit_no_hint_workspace(workspace)
    for name in EVALUATOR_ONLY_PATHS:
        if (workspace / name).exists():
            leaks.append(f"workspace:{name}")
    task_text = task_file.read_text(encoding="utf-8")
    redacted = _load_json(workspace / "metadata.json")
    leaks.extend(_walk_hint_keys(redacted, "metadata"))
    redacted_text = json.dumps(redacted, sort_keys=True)
    target_api_paths = _target_api_paths(metadata)
    for entrypoint in _private_entrypoints(metadata):
        if _entrypoint_visible_outside_target_api(
            task_text, entrypoint, target_api_paths
        ):
            leaks.append(f"TASK.md:value:{entrypoint}")
        if _entrypoint_visible_outside_target_api(
            redacted_text, entrypoint, target_api_paths
        ):
            leaks.append(f"metadata:value:{entrypoint}")
    repo_visible = (workspace / "repo").is_dir()
    requirements_visible = (workspace / "requirements.lock").is_file()
    shutil.rmtree(workspace)
    return {
        "status": "pass" if not leaks and repo_visible else "fail",
        "leaks": sorted(set(leaks)),
        "repo_visible": repo_visible,
        "requirements_visible": requirements_visible,
        "benchmark_tests_hidden": not any(
            leak.startswith("workspace:") for leak in leaks
        ),
    }


def _audit_no_hint_in_memory(metadata: dict[str, Any]) -> dict[str, Any]:
    from featureliftbench.agent_runner import redact_task_metadata
    from featureliftbench.task_render import render_agent_workspace_task

    redacted = redact_task_metadata(metadata)
    task_text = render_agent_workspace_task(metadata)
    leaks = _walk_hint_keys(redacted, "metadata")
    redacted_text = json.dumps(redacted, sort_keys=True)
    target_api_paths = _target_api_paths(metadata)
    for entrypoint in _private_entrypoints(metadata):
        if _entrypoint_visible_outside_target_api(
            task_text, entrypoint, target_api_paths
        ):
            leaks.append(f"TASK.md:value:{entrypoint}")
        if _entrypoint_visible_outside_target_api(
            redacted_text, entrypoint, target_api_paths
        ):
            leaks.append(f"metadata:value:{entrypoint}")
    return {
        "status": "pass" if not leaks else "fail",
        "leaks": sorted(set(leaks)),
        "repo_visible": None,
        "requirements_visible": None,
        "benchmark_tests_hidden": True,
    }


def _repository_counts(task_dir: Path) -> dict[str, int]:
    repo = task_dir / "repo"
    files = [path for path in repo.rglob("*") if path.is_file()]
    python_files = [path for path in files if path.suffix == ".py"]
    upstream_tests = [
        path
        for path in files
        if "test" in {part.lower() for part in path.relative_to(repo).parts[:-1]}
        or path.name.lower().startswith("test_")
        or path.name.lower().endswith("_test.py")
    ]
    return {
        "legacy_repo_file_count": len(files),
        "legacy_repo_python_file_count": len(python_files),
        "legacy_repo_upstream_test_file_count": len(upstream_tests),
    }


def _source_gate(
    task_id: str,
    snapshot: dict[str, Any] | None,
    repository: dict[str, Any] | None,
) -> tuple[str, list[str]]:
    if snapshot is None or repository is None:
        return "fail", ["canonical_source_registry_mapping_missing"]
    if snapshot.get("status") != "ready":
        status_to_issue = {
            "pending_revision_resolution": "source_revision_pending_resolution",
            "pending_full_materialization": "source_snapshot_pending_full_materialization",
            "pending_curated_audit": "curated_source_pending_audit",
            "blocked": "canonical_source_blocked",
        }
        return "pending", [
            status_to_issue.get(
                str(snapshot.get("status")),
                "canonical_source_not_ready",
            )
        ]
    required = (
        "archive_path",
        "archive_sha256",
        "source_tree_sha256",
        "license_text_path",
        "tracked_file_count",
        "python_file_count",
        "python_loc",
        "total_bytes",
        "max_path_depth",
    )
    missing = [key for key in required if snapshot.get(key) is None]
    if snapshot.get("target_snapshot_scope") == "full_tracked_tree":
        resolved = str(snapshot.get("resolved_commit") or "")
        if len(resolved) != 40:
            missing.append("resolved_commit")
    if missing:
        return "fail", [
            "ready_source_missing_evidence:" + ",".join(sorted(set(missing)))
        ]
    if task_id not in snapshot.get("task_ids", []):
        return "fail", ["canonical_source_task_membership_missing"]
    return "pass", []


def _compactness_implementation_status() -> dict[str, Any]:
    scoring_path = ROOT / "harness" / "featureliftbench" / "scoring.py"
    text = scoring_path.read_text(encoding="utf-8")
    legacy_formula = (
        "functional_gate_score * (1.0 - extraction_ratio)" in text
        and 'metrics.get("source_loc"' in text
    )
    reference_relative = (
        '"reference_relative_loc_ratio"' in text
        and '"compactness_score"' in text
        and '"final_score": float(functional_gate_score)' in text
        and 'scoring_reference.get("oracle_loc")' in text
    )
    return {
        "status": (
            "fail"
            if legacy_formula
            else "pass"
            if reference_relative
            else "unknown"
        ),
        "implementation": str(scoring_path.relative_to(ROOT)),
        "legacy_source_loc_denominator_detected": legacy_formula,
        "reference_relative_metric_detected": reference_relative,
        "required_fix": (
            "report compactness independently relative to a frozen reference or "
            "reference support set"
        ),
    }


def _v2_freeze_status(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {
            "status": "pending",
            "path": str(path.relative_to(ROOT)),
            "reason": "v2 source/spec/evaluator/environment freeze is missing",
        }
    payload = _load_json(path)
    task_ids = payload.get("tasks")
    task_count = len(task_ids) if isinstance(task_ids, (dict, list)) else 0
    ready = (
        task_count == 150
        and payload.get("policy_id") == POLICY_ID
        and payload.get("gate_pass") is True
    )
    return {
        "status": "pass" if ready else "fail",
        "path": str(path.relative_to(ROOT)),
        "task_count": task_count,
        "freeze_id": payload.get("freeze_id"),
        "reason": "" if ready else "v2 freeze exists but does not pass all gates",
    }


def _principle_summary(tasks: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts = Counter(str(task["principles"][key]) for task in tasks)
    return {
        status: counts.get(status, 0)
        for status in ("pass", "partial", "pending", "fail")
    }


def audit(
    *,
    tasks_root: Path,
    source_registry_path: Path,
    spec_freeze_path: Path,
    v2_freeze_path: Path,
    materialize_workspaces: bool,
) -> dict[str, Any]:
    registry = _load_json(source_registry_path)
    repositories, task_snapshots = _registry_indexes(registry)
    legacy_freeze = _load_json(spec_freeze_path)
    legacy_freeze_tasks = (
        legacy_freeze.get("tasks")
        if isinstance(legacy_freeze.get("tasks"), dict)
        else {}
    )
    compactness = _compactness_implementation_status()
    v2_freeze = _v2_freeze_status(v2_freeze_path)
    task_dirs = _task_dirs(tasks_root)
    tasks: list[dict[str, Any]] = []

    temporary = tempfile.TemporaryDirectory(prefix="flb-v2-audit-")
    scratch_root = Path(temporary.name)
    try:
        for task_dir in task_dirs:
            metadata = load_metadata(task_dir).data
            task_id = task_dir.name
            validation = validate_task(task_dir)
            snapshot = task_snapshots.get(task_id)
            repository = (
                repositories.get(str(snapshot.get("source_repo_id")))
                if isinstance(snapshot, dict)
                else None
            )
            source_status, source_issues = _source_gate(
                task_id,
                snapshot,
                repository,
            )
            no_hint = (
                _audit_workspace(task_dir, metadata, scratch_root)
                if materialize_workspaces
                else _audit_no_hint_in_memory(metadata)
            )

            freeze_record = legacy_freeze_tasks.get(task_id)
            legacy_freeze_matches = (
                isinstance(freeze_record, dict)
                and freeze_record.get("spec_hash") == metadata.get("spec_hash")
                and freeze_record.get("generated_task_hash")
                == metadata.get("generated_task_hash")
            )
            contract_pass = (
                validation.valid
                and metadata.get("spec_status") == SPEC_STATUS_COMPLIANT
                and legacy_freeze_matches
            )
            blockers = list(source_issues)
            if not contract_pass:
                blockers.append("contract_or_package_validation_failed")
            if no_hint["status"] != "pass":
                blockers.append("no_hint_workspace_failed")

            v2_oracle_status = (
                "pass"
                if source_status == "pass" and v2_freeze["status"] == "pass"
                else "pending"
            )
            if v2_oracle_status != "pass":
                blockers.append("v2_oracle_isolation_revalidation_pending")
            if compactness["status"] != "pass":
                blockers.append("compactness_reference_relative_not_implemented")
            if v2_freeze["status"] != "pass":
                blockers.append("v2_freeze_missing")
            principles = {
                "p1_full_repository_input": source_status,
                "p2_complete_public_contract": (
                    "pass" if contract_pass else "fail"
                ),
                "p3_no_source_location_hints": no_hint["status"],
                "p4_agent_autonomous_workflow": (
                    "pass"
                    if source_status == "pass" and no_hint["status"] == "pass"
                    else "pending"
                ),
                "p5_independent_submission": v2_oracle_status,
                "p6_functional_pass_at_1_primary": (
                    "pass" if v2_freeze["status"] == "pass" else "partial"
                ),
                "p7_compactness_independent_reference_relative": compactness[
                    "status"
                ],
                "p8_explicit_frozen_experiment_conditions": v2_freeze["status"],
            }
            has_reject_issue = (
                not validation.valid
                and any(
                    "fabricat" in error.lower()
                    or "hidden" in error.lower() and "undeclared" in error.lower()
                    for error in validation.errors
                )
            )
            verdict = (
                "reject"
                if has_reject_issue
                else "pass"
                if all(status == "pass" for status in principles.values())
                else "fix_required"
            )
            public_spec = (
                metadata.get("public_spec")
                if isinstance(metadata.get("public_spec"), dict)
                else {}
            )
            row = {
                "task_id": task_id,
                "verdict": verdict,
                "difficulty_label": metadata.get("difficulty"),
                "difficulty_recalibration_status": (
                    "empirical_label_pending_first_v2_baseline;"
                    "not_an_admission_gate"
                ),
                "source_repo_id": (
                    snapshot.get("source_repo_id")
                    if isinstance(snapshot, dict)
                    else None
                ),
                "source_snapshot_id": (
                    snapshot.get("source_snapshot_id")
                    if isinstance(snapshot, dict)
                    else None
                ),
                "source_kind": (
                    repository.get("source_kind")
                    if isinstance(repository, dict)
                    else None
                ),
                "source_revision_kind": (
                    snapshot.get("revision_kind")
                    if isinstance(snapshot, dict)
                    else None
                ),
                "source_status": (
                    snapshot.get("status")
                    if isinstance(snapshot, dict)
                    else "missing"
                ),
                "source_gate": source_status,
                "package_validation": (
                    "pass" if validation.valid else "fail"
                ),
                "package_errors": validation.errors,
                "package_warnings": validation.warnings,
                "spec_status": metadata.get("spec_status"),
                "spec_hash": metadata.get("spec_hash"),
                "task_revision": metadata.get("task_revision"),
                "required_api_count": len(public_spec.get("required_api") or []),
                "behavior_count": len(public_spec.get("behaviors") or []),
                "legacy_v1_freeze_recorded": legacy_freeze_matches,
                "legacy_v1_oracle_tree_recorded": bool(
                    isinstance(freeze_record, dict)
                    and freeze_record.get("oracle_tree_sha256")
                ),
                "no_hint_workspace": no_hint,
                "v2_oracle_isolation_status": v2_oracle_status,
                "compactness_status": compactness["status"],
                "v2_freeze_status": v2_freeze["status"],
                "principles": principles,
                "blockers": sorted(set(blockers)),
                **_repository_counts(task_dir),
            }
            tasks.append(row)
    finally:
        temporary.cleanup()

    verdict_counts = Counter(task["verdict"] for task in tasks)
    blocker_counts = Counter(
        blocker for task in tasks for blocker in task.get("blockers", [])
    )
    source_status_counts = Counter(task["source_status"] for task in tasks)
    summary = {
        "task_count": len(tasks),
        "v2_main_ready": verdict_counts.get("pass", 0),
        "fix_required": verdict_counts.get("fix_required", 0),
        "reject": verdict_counts.get("reject", 0),
        "package_validation_pass": sum(
            task["package_validation"] == "pass" for task in tasks
        ),
        "contract_pass": sum(
            task["principles"]["p2_complete_public_contract"] == "pass"
            for task in tasks
        ),
        "no_hint_pass": sum(
            task["principles"]["p3_no_source_location_hints"] == "pass"
            for task in tasks
        ),
        "canonical_source_mapped": sum(
            task["source_snapshot_id"] is not None for task in tasks
        ),
        "full_repository_ready": sum(
            task["source_gate"] == "pass" for task in tasks
        ),
        "legacy_v1_oracle_recorded": sum(
            task["legacy_v1_oracle_tree_recorded"] for task in tasks
        ),
        "v2_oracle_isolation_ready": sum(
            task["v2_oracle_isolation_status"] == "pass" for task in tasks
        ),
        "difficulty_recalibrated_for_v2": sum(
            task["difficulty_recalibration_status"] == "pass" for task in tasks
        ),
        "source_status_counts": dict(sorted(source_status_counts.items())),
        "blocker_counts": dict(sorted(blocker_counts.items())),
    }
    principle_keys = (
        "p1_full_repository_input",
        "p2_complete_public_contract",
        "p3_no_source_location_hints",
        "p4_agent_autonomous_workflow",
        "p5_independent_submission",
        "p6_functional_pass_at_1_primary",
        "p7_compactness_independent_reference_relative",
        "p8_explicit_frozen_experiment_conditions",
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "policy_id": POLICY_ID,
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "scope": {
            "tasks_root": str(tasks_root.resolve()),
            "source_registry": str(source_registry_path.resolve()),
            "legacy_spec_freeze": str(spec_freeze_path.resolve()),
            "v2_freeze": str(v2_freeze_path.resolve()),
            "workspace_materialized_per_task": materialize_workspaces,
        },
        "overall_verdict": (
            "pass" if summary["v2_main_ready"] == len(tasks) else "fix_required"
        ),
        "acceptance_interpretation": {
            "retain_as_v1_engineering_pool": summary["contract_pass"],
            "admit_to_v2_main_now": summary["v2_main_ready"],
            "reject_for_task_defect": summary["reject"],
        },
        "global_checks": {
            "source_registry": registry.get("summary", {}),
            "legacy_spec_freeze": {
                "freeze_id": legacy_freeze.get("freeze_id"),
                "oracle_freeze_id": legacy_freeze.get("oracle_freeze_id"),
                "task_count": legacy_freeze.get("task_count"),
                "scope": "mixed_snapshot_v1 evidence only",
            },
            "compactness": compactness,
            "v2_freeze": v2_freeze,
        },
        "summary": summary,
        "principles": {
            key: _principle_summary(tasks, key) for key in principle_keys
        },
        "tasks": tasks,
    }


def _csv_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for task in report["tasks"]:
        row = {
            "task_id": task["task_id"],
            "verdict": task["verdict"],
            "source_kind": task["source_kind"],
            "source_repo_id": task["source_repo_id"],
            "source_snapshot_id": task["source_snapshot_id"],
            "source_revision_kind": task["source_revision_kind"],
            "source_status": task["source_status"],
            "package_validation": task["package_validation"],
            "contract": task["principles"]["p2_complete_public_contract"],
            "no_hint": task["principles"]["p3_no_source_location_hints"],
            "full_repository": task["principles"]["p1_full_repository_input"],
            "autonomous_workflow": task["principles"][
                "p4_agent_autonomous_workflow"
            ],
            "v2_oracle_isolation": task["v2_oracle_isolation_status"],
            "functional_metric": task["principles"][
                "p6_functional_pass_at_1_primary"
            ],
            "compactness": task["compactness_status"],
            "v2_freeze": task["v2_freeze_status"],
            "difficulty_recalibration": task["difficulty_recalibration_status"],
            "legacy_repo_files": task["legacy_repo_file_count"],
            "legacy_repo_python_files": task["legacy_repo_python_file_count"],
            "legacy_repo_upstream_tests": task[
                "legacy_repo_upstream_test_file_count"
            ],
            "required_api_count": task["required_api_count"],
            "behavior_count": task["behavior_count"],
            "blockers": ";".join(task["blockers"]),
        }
        rows.append(row)
    return rows


def _markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    v2_ready = (
        report["overall_verdict"] == "pass"
        and summary["v2_main_ready"] == summary["task_count"]
    )
    principle_names = {
        "p1_full_repository_input": "1. Full-Repository input",
        "p2_complete_public_contract": "2. Complete public contract",
        "p3_no_source_location_hints": "3. No source-location hints",
        "p4_agent_autonomous_workflow": "4. Autonomous workflow",
        "p5_independent_submission": "5. Independent submission",
        "p6_functional_pass_at_1_primary": "6. Functional Pass@1 primary",
        "p7_compactness_independent_reference_relative": "7. Reference-relative compactness",
        "p8_explicit_frozen_experiment_conditions": "8. Explicit frozen conditions",
    }
    lines = [
        "# Python-150 v2 Main Readiness Audit",
        "",
        f"**Overall verdict:** `{report['overall_verdict']}`  ",
        f"**Policy:** `{report['policy_id']}`  ",
        f"**Generated:** {report['generated_at']}",
        "",
        "## Acceptance decision",
        "",
        f"- Retain as v1 engineering/spec pool: **{summary['contract_pass']}/{summary['task_count']}**.",
        f"- No-Hint workspace pass: **{summary['no_hint_pass']}/{summary['task_count']}**.",
        f"- Canonical source mapping: **{summary['canonical_source_mapped']}/{summary['task_count']}**.",
        f"- Admit to v2 Full-Repository / No-Hint Main now: **{summary['v2_main_ready']}/{summary['task_count']}**.",
        f"- Reject for a demonstrated task defect: **{summary['reject']}/{summary['task_count']}**.",
        "",
        (
            "All 150 retained task definitions now satisfy the v2 source, contract, "
            "No-Hint, Oracle/isolation, compactness and freeze gates. Historical v1 "
            "results remain a separate evidence version."
            if v2_ready
            else
            "The task definitions remain a valid engineering/spec pool, but only tasks "
            "with complete source, compactness, post-migration Oracle/isolation and v2 "
            "freeze evidence may enter Main."
        ),
        "",
        "## Eight principles",
        "",
        "| Principle | Pass | Partial | Pending | Fail |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for key, name in principle_names.items():
        counts = report["principles"][key]
        lines.append(
            f"| {name} | {counts['pass']} | {counts['partial']} | "
            f"{counts['pending']} | {counts['fail']} |"
        )
    lines.extend(
        [
            "",
            "## Main blockers",
            "",
            "| Blocker | Tasks |",
            "| --- | ---: |",
        ]
    )
    for blocker, count in sorted(
        summary["blocker_counts"].items(),
        key=lambda item: (-item[1], item[0]),
    ):
        lines.append(f"| `{blocker}` | {count} |")
    if not summary["blocker_counts"]:
        lines.append("| none | 0 |")
    lines.extend(
        [
            "",
            "## Canonical source status",
            "",
            "| Registry source status | Tasks | Meaning |",
            "| --- | ---: | --- |",
        ]
    )
    source_meanings = {
        "pending_full_materialization": "Exact commit recorded; complete tracked tree and digests still needed.",
        "pending_revision_resolution": "Historical version/tag/installed snapshot must first resolve to an exact commit.",
        "pending_curated_audit": "Curated source requires tree digest, license, and scope audit.",
        "ready": "Canonical full source evidence complete.",
        "blocked": "Source cannot currently satisfy policy.",
        "missing": "No canonical registry mapping.",
    }
    for status, count in summary["source_status_counts"].items():
        lines.append(
            f"| `{status}` | {count} | {source_meanings.get(status, 'Review required.')} |"
        )
    lines.extend(
        [
            "",
            "## Evidence boundary",
            "",
            f"- Legacy spec freeze: `{report['global_checks']['legacy_spec_freeze']['freeze_id']}`.",
            f"- Legacy Oracle freeze: `{report['global_checks']['legacy_spec_freeze']['oracle_freeze_id']}`.",
            "- Those freezes prove the mixed-snapshot v1 task/evaluator state, not the "
            "post-migration v2 source context.",
            (
                f"- Active v2 benchmark freeze: "
                f"`{report['global_checks']['v2_freeze']['freeze_id']}`."
                if v2_ready
                else
                "- A passing v2 benchmark freeze is still required."
            ),
            (
                "- Functional Pass@1 and reference-relative compactness are implemented "
                "as separate metrics."
                if report["global_checks"]["compactness"]["status"] == "pass"
                else
                "- Reference-relative compactness is not yet ready."
            ),
            "- Current `hard` labels are design labels; empirical difficulty should be "
            "recalibrated after the first frozen v2 baseline.",
            "",
            "## Per-task verdicts",
            "",
            "| Task | Source kind | Source status | Contract | No-Hint | v2 Oracle/isolation | Compactness | Verdict |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for task in report["tasks"]:
        lines.append(
            f"| `{task['task_id']}` | {task['source_kind'] or 'missing'} | "
            f"`{task['source_status']}` | "
            f"{task['principles']['p2_complete_public_contract']} | "
            f"{task['principles']['p3_no_source_location_hints']} | "
            f"{task['v2_oracle_isolation_status']} | "
            f"{task['compactness_status']} | `{task['verdict']}` |"
        )
    lines.extend(
        [
            "",
            (
                "## Next operational steps"
                if v2_ready
                else
                "## Required next acceptance sequence"
            ),
            "",
            *(
                [
                    "1. Run the Full-Repository / No-Hint Python-150 model baseline "
                    "against the active freeze.",
                    "2. Report evaluator Functional Pass@1 separately from Agent "
                    "completion and process failures.",
                    "3. Generate reference-relative compactness, token, step, latency "
                    "and failure analyses.",
                    "4. Recalibrate empirical difficulty after the frozen baseline.",
                ]
                if v2_ready
                else
                [
                    "1. Resolve all source registry blockers and materialize complete "
                    "source trees.",
                    "2. Pass contract, No-Hint, Oracle/isolation, compactness and "
                    "determinism gates.",
                    "3. Freeze source/spec/reference/evaluator/environment before model "
                    "execution.",
                ]
            ),
            "",
        ]
    )
    return "\n".join(lines)


def write_report(
    report: dict[str, Any],
    *,
    json_out: Path,
    csv_out: Path,
    markdown_out: Path,
) -> None:
    for path in (json_out, csv_out, markdown_out):
        path.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    rows = _csv_rows(report)
    with csv_out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    markdown_out.write_text(_markdown(report), encoding="utf-8")


def main() -> int:
    args = _parse_args()
    report = audit(
        tasks_root=args.tasks_root.resolve(),
        source_registry_path=args.source_registry.resolve(),
        spec_freeze_path=args.spec_freeze.resolve(),
        v2_freeze_path=args.v2_freeze.resolve(),
        materialize_workspaces=not args.skip_workspace_materialization,
    )
    write_report(
        report,
        json_out=args.json_out.resolve(),
        csv_out=args.csv_out.resolve(),
        markdown_out=args.markdown_out.resolve(),
    )
    summary = report["summary"]
    print(
        "FeatureLiftBench v2 audit: "
        f"v2-ready {summary['v2_main_ready']}/{summary['task_count']}; "
        f"contract {summary['contract_pass']}/{summary['task_count']}; "
        f"No-Hint {summary['no_hint_pass']}/{summary['task_count']}; "
        f"full-source {summary['full_repository_ready']}/{summary['task_count']}; "
        f"reject {summary['reject']}/{summary['task_count']}"
    )
    print(args.markdown_out.resolve())
    if args.strict_v2 and summary["v2_main_ready"] != summary["task_count"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
