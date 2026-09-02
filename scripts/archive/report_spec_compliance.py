#!/usr/bin/env python3
"""Summarize constitution compliance across a task split."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def load_metadata(task_dir: Path) -> dict:
    return json.loads((task_dir / "metadata.json").read_text(encoding="utf-8"))


def summarize(tasks_root: Path) -> tuple[list[dict], Counter]:
    rows: list[dict] = []
    counts: Counter = Counter()
    for task_dir in sorted(path for path in tasks_root.iterdir() if path.is_dir()):
        metadata_path = task_dir / "metadata.json"
        if not metadata_path.is_file():
            continue
        metadata = load_metadata(task_dir)
        status = metadata.get("spec_status")
        if status not in {"legacy", "compliant"}:
            status = "compliant" if isinstance(metadata.get("public_spec"), dict) else "legacy"
        counts[status] += 1
        rows.append(
            {
                "task_id": task_dir.name,
                "spec_status": status,
                "spec_hash": metadata.get("spec_hash", ""),
                "task_revision": metadata.get("task_revision", ""),
            }
        )
    return rows, counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "tasks_root",
        type=Path,
        nargs="?",
        default=Path("benchmark/tasks"),
        help="task split root (default: benchmark/tasks)",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        help="optional CSV output path",
    )
    args = parser.parse_args()
    root = args.tasks_root.resolve()
    rows, counts = summarize(root)
    print(f"tasks_root={root}")
    print(f"total={len(rows)}")
    for status in ("compliant", "legacy"):
        print(f"{status}={counts.get(status, 0)}")
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["task_id", "spec_status", "spec_hash", "task_revision"])
            writer.writeheader()
            writer.writerows(rows)
        print(f"wrote {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
