#!/usr/bin/env python3
"""Scaffold batch-5 benchmark tasks (repo snapshots and common files)."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VIBE_SOURCE = ROOT / "benchmark" / "sources" / "vibe_app"
PLUGGY_SOURCE = ROOT / "benchmark" / "tasks" / "pluggy__hook_call_order__001" / "repo"
NX_SOURCE = ROOT / "benchmark" / "sources" / "networkx_dag_curated" / "networkx"
JSON5_SOURCE = Path("/Users/chz/anaconda3/lib/python3.12/site-packages/json5")

VIBE_TASKS = [
    "vibe_app__orm_query_ast_core__001",
    "vibe_app__plugin_registry_core__001",
]

OTHER_TASKS = [
    "networkx__dag_topo_core__001",
    "json5__parse_core__001",
    "pluggy__hook_specs_core__001",
]


def copy_vibe_repo(task_dir: Path) -> None:
    dst = task_dir / "repo"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(
        VIBE_SOURCE,
        dst,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"),
    )


def copy_pluggy_repo(task_dir: Path) -> None:
    dst = task_dir / "repo"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(
        PLUGGY_SOURCE,
        dst,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"),
    )


def copy_networkx_repo(task_dir: Path) -> None:
    dst = task_dir / "repo" / "networkx"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(
        NX_SOURCE,
        dst,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"),
    )


def copy_json5_repo(task_dir: Path) -> None:
    dst = task_dir / "repo" / "json5"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(
        JSON5_SOURCE,
        dst,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache", "tool.py", "__main__.py", "arg_parser.py", "host.py"),
    )


def write_common(task_dir: Path, forbidden: str) -> None:
    (task_dir / "requirements.lock").write_text("", encoding="utf-8")
    eval_dir = task_dir / "evaluation"
    eval_dir.mkdir(parents=True, exist_ok=True)
    (eval_dir / "forbidden_imports.txt").write_text(f"{forbidden}\n", encoding="utf-8")


def prepare_task(task_id: str) -> None:
    task_dir = ROOT / "benchmark" / "tasks" / task_id
    for sub in ("public_tests", "hidden_tests", "evaluation"):
        (task_dir / sub).mkdir(parents=True, exist_ok=True)

    if task_id.startswith("vibe_app__"):
        copy_vibe_repo(task_dir)
        write_common(task_dir, "vibe_app")
    elif task_id == "networkx__dag_topo_core__001":
        copy_networkx_repo(task_dir)
        write_common(task_dir, "networkx")
    elif task_id == "json5__parse_core__001":
        copy_json5_repo(task_dir)
        write_common(task_dir, "json5")
    elif task_id == "pluggy__hook_specs_core__001":
        copy_pluggy_repo(task_dir)
        write_common(task_dir, "pluggy")


def main() -> None:
    for task_id in VIBE_TASKS + OTHER_TASKS:
        prepare_task(task_id)
        print(f"Prepared {task_id}")


if __name__ == "__main__":
    main()
