#!/usr/bin/env python3
"""Verify that the frozen Python-150 task and source data are unchanged."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from build_v3_benchmark_freeze import _tree_digest  # noqa: E402


FREEZE_PATH = ROOT / "artifacts/research_analysis/v3/current_benchmark_freeze.json"
TASK_ROOT = ROOT / "benchmark/tasks"
REGISTRY_PATH = ROOT / "benchmark/sources/registry.json"
# Contract-hardened Python-150 freeze (2026-09-01). Ancestor 846b8147 predates
# the hardening and matches only 102/150 of the current baseline packages; runs
# executed against it must be interpreted with that ancestor, not this freeze.
EXPECTED_FREEZE_ID = "0b106842710368a497b49b7f6714e0dfea54778d1fb2dae38c93ea449b339542"


def main() -> int:
    freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    if freeze.get("freeze_id") != EXPECTED_FREEZE_ID or freeze.get("gate_pass") is not True:
        raise SystemExit("active Python-150 freeze identity is not the approved freeze")
    frozen_tasks = freeze.get("tasks", {})
    task_ids = {
        path.name
        for path in TASK_ROOT.iterdir()
        if path.is_dir() and (path / "metadata.json").is_file()
    }
    if len(task_ids) != 150 or task_ids != set(frozen_tasks):
        raise SystemExit("Python-150 task membership drifted")
    source_by_task = {
        task_id: snapshot
        for snapshot in registry.get("snapshots", [])
        for task_id in snapshot.get("task_ids", [])
    }
    failures: list[str] = []
    for task_id in sorted(task_ids):
        task_dir = TASK_ROOT / task_id
        metadata = json.loads((task_dir / "metadata.json").read_text(encoding="utf-8"))
        record = frozen_tasks[task_id]
        if _tree_digest(task_dir) != record.get("task_tree"):
            failures.append(f"{task_id}: task tree drift")
        if metadata.get("spec_hash") != record.get("spec_hash"):
            failures.append(f"{task_id}: spec hash drift")
        if metadata.get("generated_task_hash") != record.get("generated_task_hash"):
            failures.append(f"{task_id}: generated TASK hash drift")
        snapshot = source_by_task.get(task_id)
        if not snapshot:
            failures.append(f"{task_id}: source registry mapping missing")
        elif (
            snapshot.get("source_snapshot_id") != record.get("source_snapshot_id")
            or snapshot.get("source_tree_sha256") != record.get("source_tree_sha256")
            or snapshot.get("archive_sha256") != record.get("source_archive_sha256")
        ):
            failures.append(f"{task_id}: source freeze drift")
    for failure in failures:
        print(f"ERROR {failure}")
    print(f"Python-150 baseline freeze: {150 - len(failures)}/150 unchanged")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
