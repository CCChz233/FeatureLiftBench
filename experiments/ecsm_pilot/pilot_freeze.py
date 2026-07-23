#!/usr/bin/env python3
"""Create, verify, and revise the immutable ECSM-Prompt pilot freeze."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
HARNESS_ROOT = REPO_ROOT / "harness"
if str(HARNESS_ROOT) not in sys.path:
    sys.path.insert(0, str(HARNESS_ROOT))

from featureliftbench.freeze import file_manifest, manifest_digest, sha256_file  # noqa: E402

DEFAULT_MANIFEST = Path(__file__).with_name("pilot_manifest.yaml")
DEFAULT_FREEZE = Path(__file__).with_name("pilot_freeze_manifest.json")
DEFAULT_RELEASE_GATE = REPO_ROOT / "artifacts/research_analysis/v1_1/release_gate_report.json"
GLOBAL_PATHS = (
    REPO_ROOT / "harness/featureliftbench/agent_runner.py",
    REPO_ROOT / "harness/featureliftbench/openhands_runner.py",
    REPO_ROOT / "harness/featureliftbench/llm_usage_proxy.py",
    REPO_ROOT / "harness/featureliftbench/evaluator.py",
    REPO_ROOT / "harness/featureliftbench/docker_eval.py",
    REPO_ROOT / "harness/featureliftbench/scoring.py",
    REPO_ROOT / "harness/featureliftbench/closure_gold.py",
    REPO_ROOT / "harness/featureliftbench/compactness.py",
    REPO_ROOT / "harness/featureliftbench/schemas",
    REPO_ROOT / "harness/config/agents.toml",
    Path(__file__).with_name("run_pilot.py"),
    Path(__file__).with_name("analyze_pilot.py"),
    Path(__file__).with_name("pilot_freeze.py"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    create = subparsers.add_parser("create")
    create.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    create.add_argument("--output", type=Path, default=DEFAULT_FREEZE)
    create.add_argument("--release-gate-report", type=Path, default=DEFAULT_RELEASE_GATE)
    verify = subparsers.add_parser("verify")
    verify.add_argument("freeze", type=Path, nargs="?", default=DEFAULT_FREEZE)
    verify.add_argument("--task-id", action="append", default=[])
    revise = subparsers.add_parser("revise")
    revise.add_argument("freeze", type=Path, nargs="?", default=DEFAULT_FREEZE)
    revise.add_argument("--scope", choices=["task", "global"], required=True)
    revise.add_argument("--task-id", action="append", default=[])
    revise.add_argument("--reason", required=True)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected YAML mapping: {path}")
    return payload


def tree_digest(path: Path) -> dict[str, Any]:
    files = file_manifest([path], root=path)
    return {"sha256": manifest_digest({"files": files}), "file_count": len(files)}


def docker_identity(image: str) -> dict[str, Any]:
    completed = subprocess.run(
        ["docker", "image", "inspect", image], capture_output=True, text=True, check=False
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or f"cannot inspect Docker image: {image}")
    values = json.loads(completed.stdout)
    value = values[0]
    digests = value.get("RepoDigests") if isinstance(value.get("RepoDigests"), list) else []
    image_id = str(value.get("Id") or "")
    return {
        "requested_ref": image,
        "image_id": image_id,
        "repo_digests": [str(item) for item in digests],
        "immutable_ref": str(digests[0]) if digests else image_id,
    }


def build_pilot_freeze(manifest_path: Path, *, revision: int) -> dict[str, Any]:
    manifest_path = manifest_path.resolve()
    manifest = load_yaml(manifest_path)
    tasks = manifest.get("tasks") if isinstance(manifest.get("tasks"), list) else []
    task_dirs = {
        str(item["task_id"]): REPO_ROOT / str(item["task_dir"])
        for item in tasks
        if isinstance(item, dict)
    }
    controls = manifest.get("controls") if isinstance(manifest.get("controls"), dict) else {}
    global_paths = GLOBAL_PATHS + (manifest_path,)
    payload: dict[str, Any] = {
        "schema_version": "featureliftbench.ecsm_pilot_freeze.v1",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "pilot_id": manifest.get("pilot_id"),
        "pilot_revision": revision,
        "pilot_manifest": manifest_path.relative_to(REPO_ROOT).as_posix(),
        "pilot_manifest_sha256": sha256_file(manifest_path),
        "task_ids": list(task_dirs),
        "task_trees": {task_id: tree_digest(path) for task_id, path in task_dirs.items()},
        "global_files": file_manifest(global_paths, root=REPO_ROOT),
        "docker": docker_identity(str(controls.get("eval_docker_image") or "featureliftbench-eval:latest")),
        "controls": {
            key: controls.get(key)
            for key in (
                "model", "agent", "agent_profile", "agent_backend", "eval_backend",
                "context_window_tokens", "reserved_output_tokens", "per_instance_total_token_budget",
                "max_steps", "timeout_seconds", "temperature", "seeds", "tools",
                "test_permissions", "submission_protocol", "network_for_agent", "network_for_evaluator",
            )
        },
        "mutation_policy": {
            "task_local_change": "supersede and rerun all seven arms for that task",
            "global_change": "supersede and rerun all arms for every started task",
            "overwrite_previous_results": False,
        },
    }
    if DEFAULT_RELEASE_GATE.is_file():
        release_gate = load_json(DEFAULT_RELEASE_GATE)
        payload["release_gate_report"] = DEFAULT_RELEASE_GATE.relative_to(REPO_ROOT).as_posix()
        payload["release_gate_report_sha256"] = sha256_file(DEFAULT_RELEASE_GATE)
        payload["evidence_status"] = release_gate.get("pilot_evidence_status")
        payload["paper_release_ready_at_freeze"] = release_gate.get("paper_release_ready") is True
    payload["freeze_id"] = manifest_digest(payload)[:16]
    return payload


def verify_pilot_freeze(
    payload: dict[str, Any], *, task_ids: list[str] | None = None
) -> list[dict[str, str]]:
    mismatches: list[dict[str, str]] = []
    manifest_path = REPO_ROOT / str(payload["pilot_manifest"])
    if sha256_file(manifest_path) != payload["pilot_manifest_sha256"]:
        mismatches.append({"scope": "pilot_manifest", "id": "global"})
    release_gate_path = REPO_ROOT / str(payload.get("release_gate_report") or "")
    if (
        not release_gate_path.is_file()
        or sha256_file(release_gate_path) != payload.get("release_gate_report_sha256")
    ):
        mismatches.append({"scope": "release_gate_report", "id": "global"})
    current_global = file_manifest(GLOBAL_PATHS + (manifest_path,), root=REPO_ROOT)
    if current_global != payload["global_files"]:
        mismatches.append({"scope": "global_files", "id": "global"})
    selected = task_ids or list(payload["task_ids"])
    manifest = load_yaml(manifest_path)
    task_dirs = {
        str(item["task_id"]): REPO_ROOT / str(item["task_dir"])
        for item in manifest.get("tasks") or []
        if isinstance(item, dict)
    }
    for task_id in selected:
        actual = tree_digest(task_dirs[task_id])
        if actual != payload["task_trees"].get(task_id):
            mismatches.append({"scope": "task", "id": task_id})
    current_docker = docker_identity(str(payload["docker"]["immutable_ref"]))
    if current_docker["image_id"] != payload["docker"]["image_id"]:
        mismatches.append({"scope": "docker", "id": "global"})
    return mismatches


def create_command(args: argparse.Namespace) -> int:
    if args.output.exists():
        raise FileExistsError(f"pilot freeze already exists: {args.output}; use revise")
    release_gate = load_json(args.release_gate_report)
    release_paths = [REPO_ROOT / value for value in release_gate.get("release_input_files") or {}]
    current_release_inputs = file_manifest(release_paths, root=REPO_ROOT)
    if current_release_inputs != release_gate.get("release_input_files"):
        raise SystemExit(
            "pilot freeze refused: release gate report is stale; rebuild audit status, review queue, and release gates"
        )
    if release_gate.get("pilot_freeze_ready") is not True:
        failed = [
            item.get("gate")
            for item in release_gate.get("gates") or []
            if isinstance(item, dict) and item.get("satisfied") is not True
        ]
        raise SystemExit(
            "pilot freeze refused: v1.1 release gates are incomplete: "
            + ", ".join(str(value) for value in failed)
        )
    payload = build_pilot_freeze(args.manifest, revision=1)
    payload["release_gate_report"] = args.release_gate_report.resolve().relative_to(REPO_ROOT).as_posix()
    payload["release_gate_report_sha256"] = sha256_file(args.release_gate_report.resolve())
    write_json(args.output, payload)
    write_json(args.output.with_name("pilot_change_ledger.json"), {
        "schema_version": "featureliftbench.ecsm_pilot_change_ledger.v1",
        "changes": [],
    })
    print(args.output)
    return 0


def verify_command(args: argparse.Namespace) -> int:
    payload = load_json(args.freeze)
    mismatches = verify_pilot_freeze(payload, task_ids=args.task_id or None)
    print(json.dumps({"freeze_id": payload["freeze_id"], "mismatches": mismatches}, indent=2))
    return 1 if mismatches else 0


def revise_command(args: argparse.Namespace) -> int:
    path = args.freeze.resolve()
    old = load_json(path)
    if args.scope == "task" and not args.task_id:
        raise ValueError("--scope task requires at least one --task-id")
    affected = list(old["task_ids"] if args.scope == "global" else args.task_id)
    unknown = sorted(set(affected) - set(old["task_ids"]))
    if unknown:
        raise ValueError(f"unknown pilot tasks: {', '.join(unknown)}")
    archive = path.with_name(f"pilot_freeze_manifest.revision-{old['pilot_revision']}.json")
    shutil.copy2(path, archive)
    manifest_path = REPO_ROOT / str(old["pilot_manifest"])
    new = build_pilot_freeze(manifest_path, revision=int(old["pilot_revision"]) + 1)
    manifest = load_yaml(manifest_path)
    execution = manifest.get("execution") if isinstance(manifest.get("execution"), dict) else {}
    run_root = REPO_ROOT / str(execution.get("output_root") or "experiments/ecsm_pilot/runs") / str(manifest.get("pilot_id"))
    superseded = []
    for task_id in affected:
        for cell in run_root.glob(f"revision-*/*/{task_id}/seed-*"):
            if (cell / "run.json").is_file():
                marker = {
                    "schema_version": "featureliftbench.ecsm_superseded_cell.v1",
                    "task_id": task_id,
                    "reason": args.reason,
                    "old_freeze_id": old["freeze_id"],
                    "new_freeze_id": new["freeze_id"],
                    "scope": args.scope,
                }
                write_json(cell / "superseded.json", marker)
                superseded.append(cell.relative_to(REPO_ROOT).as_posix())
    ledger_path = path.with_name("pilot_change_ledger.json")
    ledger = load_json(ledger_path)
    ledger.setdefault("changes", []).append({
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "scope": args.scope,
        "task_ids": affected,
        "reason": args.reason,
        "old_freeze_id": old["freeze_id"],
        "new_freeze_id": new["freeze_id"],
        "superseded_cells": superseded,
    })
    write_json(ledger_path, ledger)
    write_json(path, new)
    print(f"revision={new['pilot_revision']} superseded_cells={len(superseded)}")
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "create":
        return create_command(args)
    if args.command == "verify":
        return verify_command(args)
    if args.command == "revise":
        return revise_command(args)
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
