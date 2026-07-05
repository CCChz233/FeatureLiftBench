#!/usr/bin/env python3
"""Sync copy_all Go submission from task repo snapshot."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO / "harness") not in sys.path:
    sys.path.insert(0, str(REPO / "harness"))

from build_go_oracle_submission import build_go_submission


def sync_task(task_id: str, *, task_dir: Path | None = None) -> None:
    if task_dir is None:
        for candidate in (
            REPO / "benchmark/go/tasks" / task_id,
            REPO / "benchmark/go/staging" / task_id,
            REPO / "benchmark/go/sanity" / task_id,
        ):
            if candidate.is_dir():
                task_dir = candidate
                break
    if task_dir is None:
        raise SystemExit(f"task dir not found for {task_id}")

    out_dir = build_go_submission(task_dir.resolve(), variant="copy_all")
    print(f"synced {task_id}: {len(list(out_dir.glob('*.go')))} go files")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_ids", nargs="*", help="Task IDs")
    parser.add_argument("--all-tasks", action="store_true")
    args = parser.parse_args()
    task_ids = args.task_ids
    if args.all_tasks:
        tasks_root = REPO / "benchmark/go/tasks"
        task_ids = [p.name for p in tasks_root.iterdir() if p.is_dir() and (p / "metadata.json").is_file()]
    for task_id in task_ids:
        sync_task(task_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
