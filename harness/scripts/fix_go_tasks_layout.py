#!/usr/bin/env python3
"""Fix benchmark/go/tasks layout after partial promote."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TASKS = REPO / "benchmark/go/tasks"
SANITY = REPO / "benchmark/go/sanity/hello_featurelifted__001"
STAGING_SEMVER = REPO / "benchmark/go/staging/semver__version_parse_core__001"


def fix_semver() -> None:
    dest = TASKS / "semver__version_parse_core__001"
    if dest.is_dir() and (dest / "metadata.json").is_file():
        return
    if STAGING_SEMVER.is_dir():
        shutil.copytree(STAGING_SEMVER, dest, dirs_exist_ok=True)
        return
    # recover from flattened tasks root
    dest.mkdir(parents=True, exist_ok=True)
    for name in (
        "metadata.json",
        "TASK.md",
        "repo",
        "public_tests",
        "hidden_tests",
        "evaluation",
        "environment",
    ):
        src = TASKS / name
        if src.exists():
            target = dest / name
            if target.exists():
                continue
            if src.is_dir():
                shutil.copytree(src, target)
            else:
                shutil.copy2(src, target)
    meta = dest / "metadata.json"
    if meta.is_file():
        data = json.loads(meta.read_text(encoding="utf-8"))
        data["task_id"] = "semver__version_parse_core__001"
        meta.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def cleanup_tasks_root() -> None:
    for name in (
        "metadata.json",
        "TASK.md",
        "repo",
        "public_tests",
        "hidden_tests",
        "evaluation",
        "environment",
    ):
        path = TASKS / name
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)
    weird = TASKS / " 2"
    if weird.is_dir():
        shutil.rmtree(weird)


def ensure_hello_gold() -> None:
    dest = TASKS / "hello_featurelifted__001"
    if not dest.is_dir():
        shutil.copytree(SANITY, dest)


def main() -> int:
    fix_semver()
    cleanup_tasks_root()
    ensure_hello_gold()
    names = sorted(p.name for p in TASKS.iterdir() if p.is_dir())
    print("tasks:", len(names), names)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
