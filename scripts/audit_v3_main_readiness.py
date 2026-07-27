#!/usr/bin/env python3
"""Audit the hardened External-150 Full-Repository / No-Hint Main split."""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
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
from featureliftbench.agent_runner import audit_no_hint_workspace, prepare_agent_workspace
from featureliftbench.docker_eval import _functional_mount_allowlist_pass
from featureliftbench.evaluation_capsule import (
    CAPSULE_ALLOWED_TOP_LEVEL,
    assert_capsule_allowlist,
    build_evaluation_capsule,
)
from featureliftbench.isolation_checks import find_isolation_attack_patterns
from featureliftbench.source_archive import source_indexes, tree_stats
from featureliftbench.task_spec import compute_generated_task_hash, compute_spec_hash
from featureliftbench.validate import validate_task


POLICY_ID = "featureliftbench.full_repository_no_hint_main.v3"
SOURCE_POLICY_ID = "featureliftbench.full_repository_source.v2"
SCHEMA_VERSION = "featureliftbench.v3_main_readiness.v1"
DEFAULT_JSON = ROOT / "reports" / "audits" / "v3_main_readiness.json"
DEFAULT_CSV = ROOT / "reports" / "audits" / "v3_main_readiness.csv"
DEFAULT_MD = ROOT / "reports" / "audits" / "v3_main_readiness.md"
DEFAULT_ORACLE = (
    ROOT / "reports" / "audits" / "v3_oracle_revalidation" / "summary.json"
)
DEFAULT_CANARIES = ROOT / "reports" / "audits" / "v3_adversarial_canaries.json"
EVALUATOR_ONLY_PATHS = (
    "public_tests",
    "hidden_tests",
    "evaluation",
    "reference_solution",
    "oracle",
    "sources",
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--csv-out", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--oracle-report", type=Path, default=DEFAULT_ORACLE)
    parser.add_argument("--canary-report", type=Path, default=DEFAULT_CANARIES)
    parser.add_argument(
        "--skip-workspace-materialization",
        action="store_true",
        help="development-only fast audit; strict readiness rejects this mode",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="recompute readiness without rewriting evidence; fail if JSON evidence drifted",
    )
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _task_dirs(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(
        path
        for path in root.iterdir()
        if path.is_dir() and (path / "metadata.json").is_file()
    )


def _test_functions(directory: Path) -> set[str]:
    nodeids: set[str] = set()
    if not directory.is_dir():
        return nodeids
    for path in sorted(directory.rglob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        relative = path.relative_to(directory.parent).as_posix()
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith(
                "test_"
            ):
                nodeids.add(f"{relative}::{node.name}")
            if isinstance(node, ast.ClassDef):
                for child in node.body:
                    if isinstance(
                        child, (ast.FunctionDef, ast.AsyncFunctionDef)
                    ) and child.name.startswith("test_"):
                        nodeids.add(f"{relative}::{node.name}::{child.name}")
    return nodeids


def _contract_gate(task_dir: Path, metadata: dict[str, Any]) -> tuple[bool, list[str]]:
    issues: list[str] = []
    public_spec = metadata.get("public_spec")
    if not isinstance(public_spec, dict):
        return False, ["public_spec_missing"]
    spec_hash = compute_spec_hash(public_spec)
    task_hash = compute_generated_task_hash(
        (task_dir / "TASK.md").read_text(encoding="utf-8")
    )
    if metadata.get("spec_hash") != spec_hash:
        issues.append("spec_hash_mismatch")
    if metadata.get("generated_task_hash") != task_hash:
        issues.append("generated_task_hash_mismatch")

    behavior_contract_path = task_dir / "evaluation" / "behavior_contract.json"
    if not behavior_contract_path.is_file():
        return False, issues + ["behavior_contract_missing"]
    contract = _load(behavior_contract_path)
    if contract.get("task_id") != task_dir.name:
        issues.append("behavior_contract_task_id_mismatch")
    review = contract.get("review")
    review_status = str(contract.get("review_status") or "")
    model_results_consulted = contract.get("model_results_consulted")
    if isinstance(review, dict) and "model_results_consulted" in review:
        model_results_consulted = review.get("model_results_consulted")
    if (
        not isinstance(review, dict)
        or review_status not in {"ai_assisted_reviewed", "maintainer_reviewed"}
        or model_results_consulted is True
    ):
        issues.append("contract_review_provenance_failed")

    behaviors = public_spec.get("behaviors")
    if not isinstance(behaviors, list):
        behaviors = []
    public_ids = {
        str(item.get("id"))
        for item in behaviors
        if isinstance(item, dict) and item.get("id")
    }
    isolation_behavior = public_spec.get("isolation_behavior")
    isolation_id = (
        str(isolation_behavior.get("id"))
        if isinstance(isolation_behavior, dict) and isolation_behavior.get("id")
        else ""
    )
    expected_clause_ids = set(public_ids)
    if isolation_id:
        expected_clause_ids.add(isolation_id)
    clauses = contract.get("public_clauses")
    contract_clause_ids = {
        str(item.get("behavior_id"))
        for item in clauses
        if isinstance(clauses, list)
        and isinstance(item, dict)
        and item.get("behavior_id")
    }
    if contract_clause_ids != expected_clause_ids:
        issues.append("public_clause_bidirectional_mapping_mismatch")

    mapped_test_ids: set[str] = set()
    covered_clause_ids: set[str] = set()
    for mapping_key, expected_prefix in (
        ("public_test_mappings", "public_tests/"),
        ("hidden_test_mappings", "hidden_tests/"),
    ):
        mappings = contract.get(mapping_key)
        if not isinstance(mappings, list):
            issues.append(f"{mapping_key}_missing")
            continue
        for mapping in mappings:
            if not isinstance(mapping, dict):
                issues.append(f"{mapping_key}_invalid")
                continue
            nodeid = str(mapping.get("nodeid") or "")
            if not nodeid.startswith(expected_prefix):
                issues.append(f"{mapping_key}_wrong_partition:{nodeid}")
            mapped_test_ids.add(nodeid)
            clause_ids = {
                str(value)
                for value in mapping.get("public_clause_ids", [])
                if isinstance(value, str)
            }
            if not clause_ids or not clause_ids <= expected_clause_ids:
                issues.append(f"{mapping_key}_unknown_clause:{nodeid}")
            covered_clause_ids.update(clause_ids)

    actual_tests = _test_functions(task_dir / "public_tests") | _test_functions(
        task_dir / "hidden_tests"
    )
    if actual_tests != mapped_test_ids:
        issues.append("test_nodeid_bidirectional_mapping_mismatch")
    if not public_ids <= covered_clause_ids:
        issues.append("public_behavior_without_test_mapping")
    if isolation_id and isolation_id not in contract_clause_ids:
        issues.append("isolation_clause_missing")
    required_api = public_spec.get("required_api")
    if not isinstance(required_api, list) or not required_api:
        issues.append("required_api_missing")
    if not any(
        "required_api_surface" in nodeid
        for nodeid in mapped_test_ids
    ):
        issues.append("required_api_surface_test_unmapped")
    return not issues, sorted(set(issues))


def _workspace_gate(
    task_dir: Path,
    metadata: dict[str, Any],
    snapshot: dict[str, Any],
    scratch: Path,
    *,
    materialize: bool,
) -> tuple[bool, dict[str, Any], list[str]]:
    if not materialize:
        return False, {"materialized": False}, ["workspace_materialization_skipped"]
    workspace = scratch / task_dir.name
    issues: list[str] = []
    prepare_agent_workspace(
        task_dir,
        workspace,
        metadata,
        ablation=AblationOptions(
            mount_public_tests=False,
            prompt_style="standard",
            expose_source_hints=False,
            source_context="full_repository",
        ),
    )
    issues.extend(audit_no_hint_workspace(workspace))
    for name in EVALUATOR_ONLY_PATHS:
        if (workspace / name).exists():
            issues.append(f"evaluator_path_visible:{name}")
    if not (workspace / "repo").is_dir():
        issues.append("full_repository_missing")
        actual_stats = None
    else:
        actual_stats = tree_stats(workspace / "repo")
        if actual_stats.source_tree_sha256 != snapshot.get("source_tree_sha256"):
            issues.append("workspace_source_tree_digest_mismatch")
        if actual_stats.tracked_file_count != snapshot.get("tracked_file_count"):
            issues.append("workspace_source_file_count_mismatch")
    task_text = (workspace / "TASK.md").read_text(encoding="utf-8")
    redacted_text = (workspace / "metadata.json").read_text(encoding="utf-8")
    if "Source Entrypoints" in task_text or "source_entrypoints" in redacted_text:
        issues.append("source_entrypoint_hint_visible")
    if (workspace / "public_tests").exists() or (workspace / "hidden_tests").exists():
        issues.append("benchmark_tests_visible")
    details = {
        "materialized": True,
        "source_tree_sha256": (
            actual_stats.source_tree_sha256 if actual_stats is not None else None
        ),
        "tracked_file_count": (
            actual_stats.tracked_file_count if actual_stats is not None else None
        ),
        "no_hint": not any("hint" in issue.lower() for issue in issues),
        "test_blind": not any("test" in issue.lower() for issue in issues),
    }
    shutil.rmtree(workspace, ignore_errors=True)
    return not issues, details, sorted(set(issues))


def _capsule_gate(task_dir: Path, scratch: Path) -> tuple[bool, dict[str, Any], list[str]]:
    destination = scratch / f"{task_dir.name}-capsule"
    issues: list[str] = []
    manifest = build_evaluation_capsule(task_dir, destination)
    assert_capsule_allowlist(destination)
    actual_top_level = {path.name for path in destination.iterdir()}
    if not actual_top_level <= CAPSULE_ALLOWED_TOP_LEVEL:
        issues.append("capsule_allowlist_violation")
    forbidden_names = {
        "repo",
        "reference_solution",
        "oracle",
        "sources",
        "archives",
        "compactness.json",
        "closure_gold.json",
        "oracle_manifest.json",
    }
    present = {
        path.name
        for path in destination.rglob("*")
        if path.name in forbidden_names
    }
    if present:
        issues.append("capsule_private_payload_present:" + ",".join(sorted(present)))
    digest = str(manifest.get("digest") or "")
    if len(digest) != 64:
        issues.append("capsule_digest_invalid")
    shutil.rmtree(destination, ignore_errors=True)
    return not issues, {"digest": digest}, issues


def _static_isolation_canaries() -> dict[str, Any]:
    payloads = {
        "task_mount_read": 'P = "/workspace/tasks"\n',
        "source_archive_read": 'P = "/workspace/benchmark/sources/archives"\n',
        "reference_read": 'P = "/workspace/benchmark/references"\n',
        "oracle_read": 'P = "/workspace/submissions/x/oracle"\n',
    }
    records: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(prefix="flb-v3-static-canaries-") as tmp:
        root = Path(tmp)
        for name, source in payloads.items():
            submission = root / name
            submission.mkdir()
            (submission / "attack.py").write_text(source, encoding="utf-8")
            issues = find_isolation_attack_patterns(submission)
            records[name] = {
                "pass": bool(issues),
                "issues": [issue.format() for issue in issues],
            }
        symlink_submission = root / "symlink"
        symlink_submission.mkdir()
        (symlink_submission / "escape").symlink_to("/tmp")
        issues = find_isolation_attack_patterns(symlink_submission)
        records["symlink"] = {
            "pass": bool(issues),
            "issues": [issue.format() for issue in issues],
        }
    return {
        "gate_pass": all(record["pass"] for record in records.values()),
        "cases": records,
    }


def _mount_allowlist_gate() -> dict[str, Any]:
    allowed = [
        "docker",
        "run",
        "-v",
        "/host/harness:/workspace/harness:ro",
        "-v",
        "/host/wheels:/workspace/benchmark/vendor-wheels:ro",
        "-v",
        "/host/capsule:/workspace/evaluation-capsule:ro",
        "-v",
        "/host/submission:/workspace/submission:ro",
        "-v",
        "/host/output:/workspace/output:rw",
    ]
    attack_targets = (
        "/workspace/tasks/x",
        "/workspace/benchmark/sources/archives",
        "/workspace/benchmark/references",
        "/workspace/submissions/x/oracle",
        "/workspace/reference_solution",
    )
    rejected = []
    for target in attack_targets:
        rejected.append(
            not _functional_mount_allowlist_pass(
                allowed + ["-v", f"/host/private:{target}:ro"]
            )
        )
    return {
        "gate_pass": _functional_mount_allowlist_pass(allowed) and all(rejected),
        "allowed_targets_pass": _functional_mount_allowlist_pass(allowed),
        "forbidden_target_rejections": sum(rejected),
        "forbidden_target_count": len(rejected),
    }


def _evidence_gate(
    path: Path,
    *,
    expected_schema: str,
    expected_runs: int | None = None,
) -> dict[str, Any]:
    if not path.is_file():
        return {"gate_pass": False, "path": str(path), "reason": "missing"}
    payload = _load(path)
    passed = (
        payload.get("schema_version") == expected_schema
        and payload.get("policy_id") == POLICY_ID
        and payload.get("gate_pass") is True
    )
    if expected_runs is not None:
        summary = payload.get("summary")
        passed = (
            passed
            and isinstance(summary, dict)
            and summary.get("task_count") == 150
            and summary.get("repetitions", 0) >= 3
            and summary.get("passed_runs") == expected_runs
            and summary.get("stable_tasks") == 150
            and not payload.get("failed_task_ids")
            and not payload.get("unstable_task_ids")
        )
    return {
        "gate_pass": passed,
        "path": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def _selection_gate() -> dict[str, Any]:
    path = ROOT / "benchmark" / "selection" / "external150_replacement_20260727.json"
    payload = _load(path)
    rows = payload.get("rows")
    rows = rows if isinstance(rows, list) else []
    selected = [
        row for row in rows if isinstance(row, dict) and row.get("disposition") == "selected"
    ]
    domains = Counter(str(row.get("domain")) for row in selected)
    entanglements = Counter(str(row.get("primary_entanglement")) for row in selected)
    gate_pass = (
        len(rows) == 21
        and len(selected) == 7
        and payload.get("model_results_consulted") is False
        and max(domains.values(), default=0) <= 2
        and max(entanglements.values(), default=0) <= 2
        and {"application_service", "parser", "configuration", "plugin_registry"}
        <= set(domains)
    )
    return {
        "gate_pass": gate_pass,
        "candidate_count": len(rows),
        "selected_count": len(selected),
        "domain_counts": dict(sorted(domains.items())),
        "entanglement_counts": dict(sorted(entanglements.items())),
        "model_results_consulted": payload.get("model_results_consulted"),
        "ranking_snapshot": payload.get("ranking_snapshot"),
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    main_tasks = _task_dirs(ROOT / "benchmark" / "tasks")
    curated_tasks = _task_dirs(ROOT / "benchmark" / "curated" / "tasks")
    main_ids = {path.name for path in main_tasks}
    curated_ids = {path.name for path in curated_tasks}
    registry = _load(ROOT / "benchmark" / "sources" / "registry.json")
    repositories = {
        str(row.get("source_repo_id")): row
        for row in registry.get("repositories", [])
        if isinstance(row, dict)
    }
    _, task_snapshots = source_indexes(registry)
    compactness = _load(ROOT / "benchmark" / "references" / "compactness.json")
    reference_tasks = compactness.get("tasks")
    reference_tasks = reference_tasks if isinstance(reference_tasks, dict) else {}

    records: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="flb-v3-readiness-") as tmp:
        scratch = Path(tmp)
        for index, task_dir in enumerate(main_tasks, start=1):
            metadata = _load(task_dir / "metadata.json")
            task_id = task_dir.name
            issues: list[str] = []
            validation = validate_task(task_dir)
            if not validation.valid:
                issues.extend(f"validation:{item}" for item in validation.errors)
            snapshot = task_snapshots.get(task_id)
            repository = (
                repositories.get(str(snapshot.get("source_repo_id")))
                if isinstance(snapshot, dict)
                else None
            )
            source_pass = (
                isinstance(snapshot, dict)
                and isinstance(repository, dict)
                and repository.get("source_kind") == "external_oss"
                and snapshot.get("status") == "ready"
                and snapshot.get("current_snapshot_scope") == "full_tracked_tree"
                and snapshot.get("target_snapshot_scope") == "full_tracked_tree"
                and isinstance(snapshot.get("resolved_commit"), str)
                and len(str(snapshot.get("resolved_commit"))) == 40
                and isinstance(snapshot.get("archive_sha256"), str)
                and len(str(snapshot.get("archive_sha256"))) == 64
            )
            if not source_pass:
                issues.append("external_full_source_gate_failed")
            contract_pass, contract_issues = _contract_gate(task_dir, metadata)
            issues.extend(contract_issues)
            if isinstance(snapshot, dict):
                workspace_pass, workspace, workspace_issues = _workspace_gate(
                    task_dir,
                    metadata,
                    snapshot,
                    scratch,
                    materialize=not args.skip_workspace_materialization,
                )
            else:
                workspace_pass, workspace, workspace_issues = (
                    False,
                    {"materialized": False},
                    ["source_snapshot_missing"],
                )
            issues.extend(workspace_issues)
            capsule_pass, capsule, capsule_issues = _capsule_gate(task_dir, scratch)
            issues.extend(capsule_issues)
            reference = reference_tasks.get(task_id)
            compactness_pass = (
                isinstance(reference, dict)
                and isinstance(reference.get("python_loc"), int)
                and reference.get("python_loc", 0) > 0
                and isinstance(reference.get("file_count"), int)
                and reference.get("file_count", 0) > 0
                and isinstance(reference.get("reference_tree_sha256"), str)
                and len(reference.get("reference_tree_sha256")) == 64
            )
            if not compactness_pass:
                issues.append("compactness_reference_missing")
            split_pass = (
                metadata.get("benchmark_split", "external_main") == "external_main"
                and "vibe_app" not in task_id
                and task_id not in curated_ids
            )
            if not split_pass:
                issues.append("main_curated_split_contamination")
            records.append(
                {
                    "task_id": task_id,
                    "pass": not issues,
                    "validation_pass": validation.valid,
                    "source_pass": source_pass,
                    "workspace_pass": workspace_pass,
                    "contract_pass": contract_pass,
                    "capsule_pass": capsule_pass,
                    "compactness_pass": compactness_pass,
                    "split_pass": split_pass,
                    "workspace": workspace,
                    "capsule": capsule,
                    "source_snapshot_id": (
                        snapshot.get("source_snapshot_id")
                        if isinstance(snapshot, dict)
                        else None
                    ),
                    "issues": sorted(set(issues)),
                }
            )
            print(
                f"[{index:03d}/{len(main_tasks):03d}] "
                f"{'PASS' if not issues else 'FAIL'} {task_id}",
                flush=True,
            )

    static_canaries = _static_isolation_canaries()
    mount_allowlist = _mount_allowlist_gate()
    oracle_evidence = _evidence_gate(
        args.oracle_report.resolve(),
        expected_schema="featureliftbench.v3_oracle_revalidation.v1",
        expected_runs=450,
    )
    adversarial_evidence = _evidence_gate(
        args.canary_report.resolve(),
        expected_schema="featureliftbench.v3_adversarial_canaries.v1",
    )
    selection = _selection_gate()
    pruned = _load(ROOT / "benchmark" / "sources" / "pruned_registry.json")
    split_gate = (
        len(main_tasks) == 150
        and len(curated_tasks) == 7
        and not (main_ids & curated_ids)
        and set(reference_tasks) == main_ids
        and registry.get("policy_id") == SOURCE_POLICY_ID
        and (registry.get("summary") or {}).get("task_count") == 150
        and (registry.get("summary") or {}).get("curated_repository_count") == 0
        and (registry.get("summary") or {}).get("ready_snapshot_count")
        == (registry.get("summary") or {}).get("snapshot_count")
        and pruned.get("policy_id") == "featureliftbench.pruned_context.v1"
        and pruned.get("task_count") == 150
        and set((pruned.get("tasks") or {}).keys()) == main_ids
    )
    task_pass_count = sum(bool(record["pass"]) for record in records)
    gates = {
        "external_main_exact_150": len(main_tasks) == 150,
        "curated_exact_7": len(curated_tasks) == 7,
        "split_and_registry": split_gate,
        "task_readiness_150": task_pass_count == 150,
        "workspace_materialized_150": (
            not args.skip_workspace_materialization
            and sum(record["workspace_pass"] for record in records) == 150
        ),
        "functional_mount_allowlist": mount_allowlist["gate_pass"],
        "static_isolation_canaries": static_canaries["gate_pass"],
        "adversarial_docker_canaries": adversarial_evidence["gate_pass"],
        "oracle_450_stable": oracle_evidence["gate_pass"],
        "selection_protocol": selection["gate_pass"],
    }
    gate_pass = all(gates.values())
    return {
        "schema_version": SCHEMA_VERSION,
        "policy_id": POLICY_ID,
        "source_policy_id": SOURCE_POLICY_ID,
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "gate_pass": gate_pass,
        "status": "ready" if gate_pass else "fix_required",
        "gates": gates,
        "summary": {
            "main_task_count": len(main_tasks),
            "curated_task_count": len(curated_tasks),
            "task_pass_count": task_pass_count,
            "validation_pass": sum(record["validation_pass"] for record in records),
            "source_pass": sum(record["source_pass"] for record in records),
            "workspace_pass": sum(record["workspace_pass"] for record in records),
            "contract_pass": sum(record["contract_pass"] for record in records),
            "capsule_pass": sum(record["capsule_pass"] for record in records),
            "compactness_pass": sum(record["compactness_pass"] for record in records),
            "split_pass": sum(record["split_pass"] for record in records),
        },
        "global_evidence": {
            "source_registry": registry.get("summary"),
            "compactness_registry_id": compactness.get("registry_id"),
            "pruned_registry_freeze_id": pruned.get("freeze_id"),
            "mount_allowlist": mount_allowlist,
            "static_isolation_canaries": static_canaries,
            "adversarial_canaries": adversarial_evidence,
            "oracle_revalidation": oracle_evidence,
            "selection": selection,
        },
        "tasks": records,
    }


def _write_outputs(
    report: dict[str, Any],
    json_path: Path,
    csv_path: Path,
    markdown_path: Path,
) -> None:
    for path in (json_path, csv_path, markdown_path):
        path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(report, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "task_id",
                "pass",
                "validation_pass",
                "source_pass",
                "workspace_pass",
                "contract_pass",
                "capsule_pass",
                "compactness_pass",
                "split_pass",
                "issues",
            ),
            lineterminator="\n",
        )
        writer.writeheader()
        for record in report["tasks"]:
            writer.writerow(
                {
                    **{key: record[key] for key in writer.fieldnames if key != "issues"},
                    "issues": "; ".join(record["issues"]),
                }
            )
    summary = report["summary"]
    lines = [
        "# FeatureLiftBench v3 Main Readiness",
        "",
        f"- Verdict: **{'PASS' if report['gate_pass'] else 'FIX REQUIRED'}**",
        f"- External Main: {summary['main_task_count']} tasks",
        f"- Curated split: {summary['curated_task_count']} tasks",
        f"- Per-task readiness: {summary['task_pass_count']}/150",
        f"- Full-repository workspace: {summary['workspace_pass']}/150",
        f"- Contract/test mapping: {summary['contract_pass']}/150",
        f"- Source-free functional capsule: {summary['capsule_pass']}/150",
        f"- Reference-relative compactness: {summary['compactness_pass']}/150",
        "",
        "## Global gates",
        "",
    ]
    lines.extend(
        f"- {'PASS' if passed else 'FAIL'} — `{name}`"
        for name, passed in report["gates"].items()
    )
    failures = [record for record in report["tasks"] if not record["pass"]]
    if failures:
        lines.extend(["", "## Task failures", ""])
        lines.extend(
            f"- `{record['task_id']}`: {', '.join(record['issues'])}"
            for record in failures
        )
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = _parse_args()
    report = build_report(args)
    if args.check:
        json_path = args.json_out.resolve()
        if not json_path.is_file():
            print(f"missing readiness evidence: {json_path}", file=sys.stderr)
            return 1
        existing = _load(json_path)
        expected_stable = {key: value for key, value in report.items() if key != "generated_at"}
        existing_stable = {
            key: value for key, value in existing.items() if key != "generated_at"
        }
        if existing_stable != expected_stable:
            print("v3 readiness evidence drifted; rerun without --check and rebuild freeze", file=sys.stderr)
            return 1
    else:
        _write_outputs(
            report,
            args.json_out.resolve(),
            args.csv_out.resolve(),
            args.markdown_out.resolve(),
        )
    summary = report["summary"]
    print(
        f"FeatureLiftBench v3 readiness: "
        f"{'PASS' if report['gate_pass'] else 'FIX REQUIRED'}; "
        f"tasks {summary['task_pass_count']}/150; "
        f"workspaces {summary['workspace_pass']}/150; "
        f"contracts {summary['contract_pass']}/150.",
        flush=True,
    )
    if args.strict and not report["gate_pass"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
