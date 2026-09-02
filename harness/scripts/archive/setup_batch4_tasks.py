#!/usr/bin/env python3
"""Copy batch-4 OSS snapshots from site-packages into benchmark/tasks/."""

from __future__ import annotations

import importlib.metadata as metadata
import shutil
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
SITE = Path(sys.executable).resolve().parent.parent / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"

TASKS = {
    "faker__provider_core__001": ("faker", SITE / "faker"),
    "lark__grammar_loader_core__001": ("lark", SITE / "lark"),
    "rich__markup_parse_core__001": ("rich", SITE / "rich"),
    "marshmallow__schema_core__001": ("marshmallow", SITE / "marshmallow"),
    "babel__plural_core__001": ("babel", SITE / "babel"),
}

SKIP_PARTS = frozenset({"__pycache__", "tests", "testing", "benchmarks", ".github"})


def copy_package(task_id: str, package: str, src: Path, dst_repo: Path) -> str:
    if not src.is_dir():
        raise SystemExit(f"missing package source: {src}")
    if dst_repo.exists():
        shutil.rmtree(dst_repo)
    dst_pkg = dst_repo / package
    shutil.copytree(
        src,
        dst_pkg,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
    )
    version = metadata.version({"faker": "Faker", "lark": "lark", "rich": "rich", "marshmallow": "marshmallow", "babel": "Babel"}[package])
    license_dst = dst_repo / "LICENSE"
    for candidate in (
        SITE / f"{package}-{version}.dist-info" / "LICENSE",
        SITE / f"{package.replace('_', '-')}-{version}.dist-info" / "LICENSE",
        SITE / "Faker-{}.dist-info".format(version) / "LICENSE",
        SITE / "Babel-{}.dist-info".format(version) / "LICENSE",
    ):
        if candidate.is_file():
            shutil.copy2(candidate, license_dst)
            break
    return f"{version}-installed-snapshot"


def main() -> None:
    if not SITE.is_dir():
        raise SystemExit(f"site-packages not found: {SITE}")
    versions: dict[str, str] = {}
    for task_id, (package, src) in TASKS.items():
        task_dir = _REPO_ROOT / "benchmark" / "tasks" / task_id
        versions[task_id] = copy_package(task_id, package, src, task_dir / "repo")
        print(f"copied {package} -> {task_dir / 'repo' / package} ({versions[task_id]})")
    print("versions:", versions)


if __name__ == "__main__":
    main()
