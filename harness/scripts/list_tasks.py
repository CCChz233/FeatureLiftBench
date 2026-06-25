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

from featureliftbench.paths import SANITY_TASKS_DIR, TASKS_DIR
from featureliftbench.task_discovery import discover_task_dirs_under

# Convenience alias only; not a separate benchmark partition.
SKIP_DIRS = {"extreme"}


def discover_task_dirs(root: Path) -> list[Path]:
    return discover_task_dirs_under(root, hard_only=False)


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
        help="Task root directory (default: benchmark/tasks/; use benchmark/sanity for smoke)",
    )
    parser.add_argument(
        "--all-difficulties",
        action="store_true",
        help="Include easy/medium when listing benchmark/tasks/ (default: hard only)",
    )
    parser.add_argument(
        "--include-sanity",
        action="store_true",
        help="Also list tasks under benchmark/sanity/",
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
    roots = [args.root.resolve()]
    if args.include_sanity and args.root.resolve() == TASKS_DIR:
        roots.append(SANITY_TASKS_DIR)
    hard_only = not args.all_difficulties and args.root.resolve() == TASKS_DIR

    task_dirs: list[Path] = []
    for root in roots:
        if not root.is_dir():
            continue
        task_dirs.extend(
            discover_task_dirs_under(root, hard_only=hard_only if root == TASKS_DIR else False)
        )
    task_dirs = sorted({path.resolve() for path in task_dirs})

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
