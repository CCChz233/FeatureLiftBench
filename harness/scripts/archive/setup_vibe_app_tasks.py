#!/usr/bin/env python3
"""Copy sources/vibe_app into task repos and scaffold task directories."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "benchmark" / "sources" / "vibe_app"

TASKS = [
    "vibe_app__pricing_rules_core__001",
    "vibe_app__yaml_config_bootstrap__001",
    "vibe_app__csv_transform_core__001",
]

REQUIREMENTS_LOCK = ""


def copy_repo(task_dir: Path) -> None:
    dst = task_dir / "repo"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(
        SOURCE,
        dst,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"),
    )


def write_common(task_dir: Path) -> None:
    (task_dir / "requirements.lock").write_text(REQUIREMENTS_LOCK, encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("vibe_app\n", encoding="utf-8")


def setup_task(task_id: str) -> None:
    task_dir = ROOT / "benchmark" / "tasks" / task_id
    for sub in ("public_tests", "hidden_tests", "evaluation"):
        (task_dir / sub).mkdir(parents=True, exist_ok=True)
    copy_repo(task_dir)
    write_common(task_dir)


def main() -> None:
    for task_id in TASKS:
        setup_task(task_id)
        print(f"Prepared {task_id}")


if __name__ == "__main__":
    main()
