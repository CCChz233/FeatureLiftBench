#!/usr/bin/env python3
"""Bootstrap batch-2 benchmark tasks (pygments, lark, attrs)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TASKS = REPO_ROOT / "benchmark" / "tasks"
PY_SITE = Path("/Users/chz/anaconda3/lib/python3.12/site-packages")
LARK_SRC = Path("/tmp/lark-src")

PYGMENTS_VERSION = "2.15.1"
LARK_VERSION = "1.2.2"
ATTRS_VERSION = "23.1.0"

PYGMENTS_TASKS = [
    "pygments__lexer_core__001",
    "pygments__formatter_core__001",
]
LARK_TASKS = [
    "lark__parse_tree_core__001",
    "lark__visitor_transform_core__001",
]
ATTRS_TASKS = ["attrs__validators_core__001"]


def copy_pygments_repo(dst: Path) -> None:
    src = PY_SITE / "pygments"
    pkg_dst = dst / "pygments"
    if pkg_dst.exists():
        shutil.rmtree(pkg_dst)
    shutil.copytree(
        src,
        pkg_dst,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    license_src = PY_SITE / "pygments-2.15.1.dist-info" / "LICENSE"
    shutil.copy2(license_src, dst / "LICENSE")


def copy_lark_repo(dst: Path) -> None:
    src = LARK_SRC / "lark"
    pkg_dst = dst / "lark"
    if pkg_dst.exists():
        shutil.rmtree(pkg_dst)
    shutil.copytree(
        src,
        pkg_dst,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "tools", "__pyinstaller"),
    )
    shutil.copy2(LARK_SRC / "LICENSE", dst / "LICENSE")


def copy_attrs_repo(dst: Path) -> None:
    for pkg in ("attr", "attrs"):
        src = PY_SITE / pkg
        pkg_dst = dst / pkg
        if pkg_dst.exists():
            shutil.rmtree(pkg_dst)
        shutil.copytree(
            src,
            pkg_dst,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
    licenses = PY_SITE / "attrs-23.1.0.dist-info" / "licenses"
    if licenses.is_dir():
        shutil.copy2(next(licenses.iterdir()), dst / "LICENSE")
    else:
        (dst / "LICENSE").write_text("MIT\n", encoding="utf-8")


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def ensure_task_skeleton(task_id: str, repo_setup) -> None:
    task_dir = TASKS / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    repo_setup(task_dir / "repo")
    (task_dir / "requirements.lock").write_text("", encoding="utf-8")
    eval_dir = task_dir / "evaluation"
    eval_dir.mkdir(exist_ok=True)
    (eval_dir / "forbidden_imports.txt").write_text(
        {"pygments__lexer_core__001": "pygments\n", "pygments__formatter_core__001": "pygments\n",
         "lark__parse_tree_core__001": "lark\n", "lark__visitor_transform_core__001": "lark\n",
         "attrs__validators_core__001": "attrs\nattr\n"}[task_id],
        encoding="utf-8",
    )
    write_json(eval_dir / "oracle_manifest.json", {})
    for tests_dir in ("public_tests", "hidden_tests"):
        (task_dir / tests_dir).mkdir(exist_ok=True)


def main() -> None:
    for task_id in PYGMENTS_TASKS:
        ensure_task_skeleton(task_id, copy_pygments_repo)
    for task_id in LARK_TASKS:
        ensure_task_skeleton(task_id, copy_lark_repo)
    for task_id in ATTRS_TASKS:
        ensure_task_skeleton(task_id, copy_attrs_repo)
    print("Bootstrapped repos for", len(PYGMENTS_TASKS + LARK_TASKS + ATTRS_TASKS), "tasks")


if __name__ == "__main__":
    main()
