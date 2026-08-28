#!/usr/bin/env python3.12
"""Materialize Pilot swap replacements: waitress, polyfactory, graphene."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from materialize_hard50_pilot_oracles import (  # noqa: E402
    PIN_ROOT,
    PILOT,
    append_init,
    copy_repo,
    copy_rewritten,
    update_oracle_manifest,
    write_lock,
)

TEST_DIR_NAMES = {"tests", "test", "testing"}


def strip_inpackage_tests(package_root: Path) -> None:
    for path in list(package_root.rglob("*")):
        if path.is_dir() and path.name in TEST_DIR_NAMES:
            shutil.rmtree(path)


def py_files(dest: Path) -> list[str]:
    return sorted(
        str(p.relative_to(dest)).replace("\\", "/")
        for p in dest.rglob("*.py")
        if p.is_file()
    )


def materialize() -> None:
    specs = {
        "waitress__adjustments_core__001": {
            "clone": PIN_ROOT / "waitress__adjustments_core__001",
            "src_pkg": PIN_ROOT / "waitress__adjustments_core__001" / "src" / "waitress",
            "old": "waitress",
            "deps": [],
            "init": "from .adjustments import Adjustments\n",
        },
        "polyfactory__model_factory_core__001": {
            "clone": PIN_ROOT / "polyfactory__model_factory_core__001",
            "src_pkg": PIN_ROOT / "polyfactory__model_factory_core__001" / "polyfactory",
            "old": "polyfactory",
            "deps": ["faker==40.37.0", "typing-extensions==4.15.0"],
            "init": (
                "from .exceptions import ConfigurationException\n"
                "from .factories.dataclass_factory import DataclassFactory\n"
                "from .fields import Ignore, Require, Use\n"
            ),
        },
        "graphene__schema_execute_core__001": {
            "clone": PIN_ROOT / "graphene__schema_execute_core__001",
            "src_pkg": PIN_ROOT / "graphene__schema_execute_core__001" / "graphene",
            "old": "graphene",
            "deps": [
                "graphql-core==3.2.11",
                "graphql-relay==3.2.0",
                "python-dateutil==2.9.0.post0",
                "six==1.17.0",
                "typing-extensions==4.15.0",
            ],
            "init": "",
            "strip_tests": True,
        },
    }
    for task_id, spec in specs.items():
        task_dir = PILOT / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        print(f"materializing {task_id}")
        copy_repo(spec["clone"], task_dir / "repo")
        dest = task_dir / "reference_solution" / "featurelifted"
        copy_rewritten(spec["src_pkg"], dest, spec["old"], spec.get("extra"))
        if spec.get("strip_tests"):
            strip_inpackage_tests(dest)
        if spec.get("init"):
            append_init(dest, spec["init"])
        write_lock(task_dir, spec["deps"])
        (task_dir / "evaluation").mkdir(exist_ok=True)
        names = py_files(dest)
        rel = [f"{spec['old']}/{name}" for name in names[:40]]
        update_oracle_manifest(
            task_dir,
            spec["old"],
            rel,
            [line.split("==")[0] for line in spec["deps"]],
            "Import-rewritten upstream package used as oracle; in-package tests stripped when present.",
        )
        (task_dir / "evaluation" / "forbidden_imports.txt").write_text(
            spec["old"] + "\n", encoding="utf-8"
        )


if __name__ == "__main__":
    materialize()
