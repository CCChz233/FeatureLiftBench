#!/usr/bin/env python3
"""List FeatureLiftBench task directories under benchmark/tasks/."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "harness"))

from featureliftbench.paths import TASKS_DIR

# Convenience alias only; not a separate benchmark partition.
SKIP_DIRS = {"extreme"}


def discover_task_dirs(root: Path) -> list[Path]:
    if (root / "metadata.json").is_file():
        return [root.resolve()]
    if not root.is_dir():
        raise ValueError(f"task path does not exist or is not a directory: {root}")
    return sorted(
        child.resolve()
        for child in root.iterdir()
        if child.name not in SKIP_DIRS and (child / "metadata.json").is_file()
    )


def load_tags(task_dir: Path) -> list[str]:
    metadata_path = task_dir / "metadata.json"
    with metadata_path.open("r", encoding="utf-8") as handle:
        metadata = json.load(handle)
    tags = metadata.get("tags") or []
    return [tag for tag in tags if isinstance(tag, str)]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=TASKS_DIR,
        help="Task root directory (default: benchmark/tasks/)",
    )
    parser.add_argument(
        "--tag",
        action="append",
        help="Only include tasks whose metadata.tags contain this value (repeatable)",
    )
    parser.add_argument(
        "--difficulty",
        action="append",
        choices=["easy", "medium", "hard"],
        help="Only include tasks with this metadata.difficulty (repeatable)",
    )
    parser.add_argument(
        "--paths",
        action="store_true",
        help="Print task directory paths only (for scripting)",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    task_dirs = discover_task_dirs(root)

    if args.tag:
        required = set(args.tag)
        task_dirs = [
            task_dir
            for task_dir in task_dirs
            if required.issubset(set(load_tags(task_dir)))
        ]

    if args.difficulty:
        allowed = set(args.difficulty)

        def _difficulty(task_dir: Path) -> str | None:
            with (task_dir / "metadata.json").open("r", encoding="utf-8") as handle:
                metadata = json.load(handle)
            value = metadata.get("difficulty")
            return value if isinstance(value, str) else None

        task_dirs = [task_dir for task_dir in task_dirs if _difficulty(task_dir) in allowed]

    if args.paths:
        for task_dir in task_dirs:
            print(task_dir)
        return

    print(f"# FeatureLiftBench tasks: {len(task_dirs)}")
    for task_dir in task_dirs:
        with (task_dir / "metadata.json").open("r", encoding="utf-8") as handle:
            metadata = json.load(handle)
        difficulty = metadata.get("difficulty") or "-"
        task_id = metadata.get("task_id") or task_dir.name
        print(f"{task_id}\tdifficulty={difficulty}")


if __name__ == "__main__":
    main()
