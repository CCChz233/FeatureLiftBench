#!/usr/bin/env python3
"""Freeze task-local source trees for the Pruned-Context ablation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from featureliftbench.pruned_source import PRUNED_POLICY_ID
from featureliftbench.source_archive import tree_stats


ROOT = Path(__file__).resolve().parents[1]
TASKS_ROOT = ROOT / "benchmark" / "tasks"
OUTPUT = ROOT / "benchmark" / "sources" / "pruned_registry.json"


def build_payload() -> dict:
    tasks: dict[str, dict] = {}
    for task_dir in sorted(TASKS_ROOT.iterdir()):
        if not (task_dir / "metadata.json").is_file():
            continue
        source = task_dir / "repo"
        if not source.is_dir():
            raise ValueError(f"{task_dir.name}: missing task-local repo/")
        stats = tree_stats(source)
        tasks[task_dir.name] = {
            "source_snapshot_id": f"pruned__{task_dir.name}",
            "source_path": source.relative_to(ROOT).as_posix(),
            "source_tree_sha256": stats.source_tree_sha256,
            "tracked_file_count": stats.tracked_file_count,
            "python_file_count": stats.python_file_count,
            "python_loc": stats.python_loc,
        }
    canonical = json.dumps(tasks, sort_keys=True, separators=(",", ":")).encode("utf-8")
    freeze_id = hashlib.sha256(canonical).hexdigest()
    return {
        "schema_version": "featureliftbench.pruned_registry.v1",
        "policy_id": PRUNED_POLICY_ID,
        "freeze_id": freeze_id,
        "source_condition": "task-local historical snapshots; No-Hint and test-blind",
        "historical_results_label": "mixed_snapshot_v1",
        "task_count": len(tasks),
        "tasks": tasks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("pruned source registry is stale; rebuild it")
        print(f"Pruned registry verified: {payload['task_count']} tasks")
        return 0
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)} ({payload['task_count']} tasks)")
    print(f"freeze_id={payload['freeze_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
