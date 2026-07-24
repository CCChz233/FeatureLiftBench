#!/usr/bin/env python3
"""Build a compact, tracked Python-150 specification freeze artifact."""

from __future__ import annotations

import argparse
import json
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
    verify_file_manifest,
)
from featureliftbench.task_spec import (
    compute_generated_task_hash,
    compute_spec_hash,
)
from featureliftbench.validate import validate_task


DEFAULT_POINTER = (
    ROOT / "artifacts/research_analysis/v1_1/current_oracle_freeze.json"
)
DEFAULT_OUTPUT = (
    ROOT / "artifacts/research_analysis/v1_1/current_spec_freeze.json"
)


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oracle-pointer", type=Path, default=DEFAULT_POINTER)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify that the existing output has the current freeze id",
    )
    return parser.parse_args()


def _tree_digest(path: Path) -> dict[str, Any]:
    files = file_manifest([path], root=path)
    return {
        "sha256": manifest_digest({"files": files}),
        "file_count": len(files),
    }


def build_payload(pointer_path: Path) -> dict[str, Any]:
    pointer = _load(pointer_path)
    manifest_path = ROOT / str(pointer["freeze_manifest"])
    manifest = _load(manifest_path)
    freeze_root = manifest_path.parent
    canary = _load(freeze_root / "canary" / "summary.json")
    full = _load(freeze_root / "full" / "summary.json")
    quarantine = _load(freeze_root / "quarantine_manifest.json")
    oracle_freeze_id = str(manifest.get("freeze_id", ""))
    if pointer.get("freeze_id") != oracle_freeze_id:
        raise ValueError("Oracle pointer and freeze manifest disagree")
    if canary.get("freeze_id") != oracle_freeze_id or canary.get("gate_pass") is not True:
        raise ValueError("Oracle canary gate has not passed for the current freeze")
    if full.get("freeze_id") != oracle_freeze_id or full.get("gate_pass") is not True:
        raise ValueError("Oracle full gate has not passed for the current freeze")
    if quarantine.get("freeze_id") != oracle_freeze_id or quarantine.get("tasks"):
        raise ValueError("current Oracle freeze has quarantine entries")
    evaluator_mismatches = verify_file_manifest(
        manifest.get("evaluator_files", {}),
        root=ROOT,
    )
    wheel_mismatches = verify_file_manifest(
        manifest.get("vendor_wheels", {}),
        root=ROOT,
    )
    if evaluator_mismatches:
        raise ValueError(
            f"current evaluator differs from Oracle freeze: {evaluator_mismatches[:3]}"
        )
    if wheel_mismatches:
        raise ValueError(
            f"current vendor wheels differ from Oracle freeze: {wheel_mismatches[:3]}"
        )

    tasks_root = ROOT / "benchmark/tasks"
    task_dirs = sorted(
        path
        for path in tasks_root.iterdir()
        if path.is_dir() and (path / "metadata.json").is_file()
    )
    if len(task_dirs) != 150:
        raise ValueError(f"expected 150 Python tasks, found {len(task_dirs)}")

    task_records: dict[str, dict[str, Any]] = {}
    validated = 0
    hardened = 0
    independent_human_review = 0
    for task_dir in task_dirs:
        metadata = _load(task_dir / "metadata.json")
        task_id = task_dir.name
        if metadata.get("task_id") != task_id:
            raise ValueError(f"task id mismatch: {task_id}")
        if metadata.get("spec_status") != "compliant":
            raise ValueError(f"task is not compliant: {task_id}")
        public_spec = metadata.get("public_spec")
        if not isinstance(public_spec, dict):
            raise ValueError(f"task lacks public_spec: {task_id}")
        task_markdown = (task_dir / "TASK.md").read_text(encoding="utf-8")
        expected_spec_hash = compute_spec_hash(public_spec)
        expected_task_hash = compute_generated_task_hash(task_markdown)
        if metadata.get("spec_hash") != expected_spec_hash:
            raise ValueError(f"spec hash mismatch: {task_id}")
        if metadata.get("generated_task_hash") != expected_task_hash:
            raise ValueError(f"generated TASK hash mismatch: {task_id}")
        result = validate_task(task_dir)
        if not result.valid:
            raise ValueError(
                f"task validation failed: {task_id}: {'; '.join(result.errors)}"
            )
        validated += 1
        evaluation_spec = metadata.get("evaluation_spec")
        if isinstance(evaluation_spec, dict):
            if isinstance(
                evaluation_spec.get("experiment_contract_hardening"),
                dict,
            ):
                hardened += 1
            manual = evaluation_spec.get("manual_review")
            if (
                isinstance(manual, dict)
                and manual.get("independent_human_review") is True
            ):
                independent_human_review += 1
        task_tree = manifest.get("task_trees", {}).get(task_id)
        if not isinstance(task_tree, dict):
            raise ValueError(f"Oracle freeze lacks task tree: {task_id}")
        if _tree_digest(task_dir) != task_tree:
            raise ValueError(f"task tree differs from Oracle freeze: {task_id}")
        oracle_dir = ROOT / "benchmark/submissions" / task_id / "oracle"
        oracle_tree = manifest.get("oracle_trees", {}).get(task_id)
        if not isinstance(oracle_tree, dict):
            raise ValueError(f"Oracle freeze lacks Oracle tree: {task_id}")
        if _tree_digest(oracle_dir) != oracle_tree:
            raise ValueError(f"Oracle tree differs from freeze: {task_id}")
        task_records[task_id] = {
            "task_revision": metadata.get("task_revision"),
            "spec_hash": expected_spec_hash,
            "generated_task_hash": expected_task_hash,
            "task_tree_sha256": task_tree.get("sha256"),
            "oracle_tree_sha256": oracle_tree.get("sha256"),
        }

    payload: dict[str, Any] = {
        "schema_version": "featureliftbench.spec_freeze.v1",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "split": "python-main-150",
        "task_count": len(task_records),
        "oracle_freeze_id": oracle_freeze_id,
        "oracle_freeze_manifest": str(manifest_path.relative_to(ROOT)),
        "evaluator_files": manifest.get("evaluator_files", {}),
        "vendor_wheels": manifest.get("vendor_wheels", {}),
        "oracle_canary": {
            "gate_pass": canary["gate_pass"],
            "run_count": canary["run_count"],
            "expected_run_count": canary["expected_run_count"],
        },
        "oracle_full": {
            "gate_pass": full["gate_pass"],
            "run_count": full["run_count"],
            "expected_run_count": full["expected_run_count"],
            "unstable_task_ids": full["unstable_task_ids"],
            "failed_task_ids": full["failed_task_ids"],
            "invalid_artifact_task_ids": full["invalid_artifact_task_ids"],
        },
        "gates": {
            "constitution_validated": validated,
            "experiment_contract_hardened": hardened,
            "independent_human_review": independent_human_review,
            "experiment_ready": validated == 150 and hardened == 150,
            "paper_ready": (
                validated == 150
                and hardened == 150
                and independent_human_review == 150
            ),
        },
        "tasks": task_records,
    }
    payload["freeze_id"] = manifest_digest(payload)[:16]
    return payload


def verify_existing(payload: dict[str, Any]) -> None:
    expected_freeze_id = manifest_digest(payload)[:16]
    if payload.get("freeze_id") != expected_freeze_id:
        raise ValueError("tracked spec freeze digest is invalid")
    if payload.get("task_count") != 150:
        raise ValueError("tracked spec freeze does not contain Python-150")
    oracle_full = payload.get("oracle_full")
    if not isinstance(oracle_full, dict) or oracle_full.get("gate_pass") is not True:
        raise ValueError("tracked spec freeze lacks a passing Oracle full gate")
    gates = payload.get("gates")
    if not isinstance(gates, dict) or gates.get("experiment_ready") is not True:
        raise ValueError("tracked spec freeze is not experiment-ready")
    evaluator_mismatches = verify_file_manifest(
        payload.get("evaluator_files", {}),
        root=ROOT,
    )
    wheel_mismatches = verify_file_manifest(
        payload.get("vendor_wheels", {}),
        root=ROOT,
    )
    if evaluator_mismatches or wheel_mismatches:
        raise ValueError(
            "tracked evaluator or wheel files have drifted: "
            f"{(evaluator_mismatches + wheel_mismatches)[:3]}"
        )
    task_records = payload.get("tasks")
    if not isinstance(task_records, dict) or len(task_records) != 150:
        raise ValueError("tracked spec freeze task records are incomplete")
    for task_id, record in sorted(task_records.items()):
        if not isinstance(record, dict):
            raise ValueError(f"invalid tracked task record: {task_id}")
        task_dir = ROOT / "benchmark/tasks" / task_id
        metadata = _load(task_dir / "metadata.json")
        task_markdown = (task_dir / "TASK.md").read_text(encoding="utf-8")
        if metadata.get("spec_hash") != record.get("spec_hash"):
            raise ValueError(f"tracked spec hash differs: {task_id}")
        if compute_spec_hash(metadata["public_spec"]) != record.get("spec_hash"):
            raise ValueError(f"computed spec hash differs: {task_id}")
        if (
            compute_generated_task_hash(task_markdown)
            != record.get("generated_task_hash")
        ):
            raise ValueError(f"generated TASK hash differs: {task_id}")
        if _tree_digest(task_dir).get("sha256") != record.get("task_tree_sha256"):
            raise ValueError(f"task tree differs: {task_id}")
        oracle_dir = ROOT / "benchmark/submissions" / task_id / "oracle"
        if (
            _tree_digest(oracle_dir).get("sha256")
            != record.get("oracle_tree_sha256")
        ):
            raise ValueError(f"Oracle tree differs: {task_id}")
        result = validate_task(task_dir)
        if not result.valid:
            raise ValueError(
                f"task validation failed: {task_id}: {'; '.join(result.errors)}"
            )


def main() -> int:
    args = _parse_args()
    if args.check:
        existing = _load(args.output)
        verify_existing(existing)
        if args.oracle_pointer.is_file():
            payload = build_payload(args.oracle_pointer)
            if existing.get("freeze_id") != payload["freeze_id"]:
                print(
                    "spec freeze mismatch: "
                    f"expected {payload['freeze_id']}, "
                    f"found {existing.get('freeze_id')}",
                    file=sys.stderr,
                )
                return 1
        print(f"spec freeze verified: {existing['freeze_id']}")
        return 0
    payload = build_payload(args.oracle_pointer)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(args.output)
    print(
        f"spec freeze {payload['freeze_id']}: "
        f"{payload['task_count']} tasks; "
        f"Oracle {payload['oracle_full']['run_count']}/"
        f"{payload['oracle_full']['expected_run_count']}; "
        f"experiment_ready={payload['gates']['experiment_ready']}; "
        f"paper_ready={payload['gates']['paper_ready']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
