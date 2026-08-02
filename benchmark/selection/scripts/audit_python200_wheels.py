#!/usr/bin/env python3
"""Verify exact offline wheel coverage for the Python-200 runtime ABI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from packaging.requirements import Requirement
    from packaging.utils import canonicalize_name, parse_wheel_filename
except ImportError:  # pragma: no cover - pip vendors packaging in minimal setups
    from pip._vendor.packaging.requirements import Requirement
    from pip._vendor.packaging.utils import canonicalize_name, parse_wheel_filename


ROOT = Path(__file__).resolve().parents[3]
SUITE_PATH = ROOT / "benchmark/selection/python200_suite.json"
WHEEL_ROOT = ROOT / "benchmark/vendor-wheels"


def compatible(tags: object, python_version: str) -> bool:
    target = int(python_version)
    for tag in tags:
        platform = tag.platform
        linux_x86 = (
            ("manylinux" in platform or platform.startswith("linux"))
            and "x86_64" in platform
        )
        if platform == "any" and tag.interpreter.startswith("py"):
            return True
        if not linux_x86:
            continue
        if tag.interpreter.startswith("py"):
            return True
        if tag.interpreter == f"cp{python_version}":
            return True
        if (
            tag.abi == "abi3"
            and tag.interpreter.startswith("cp")
            and int(tag.interpreter[2:]) <= target
        ):
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python-version", default="311", choices=("311", "312"))
    args = parser.parse_args()
    suite = json.loads(SUITE_PATH.read_text(encoding="utf-8"))
    task_root = ROOT / suite["task_root"]
    wheels = []
    for path in WHEEL_ROOT.glob("*.whl"):
        try:
            name, version, _build, tags = parse_wheel_filename(path.name)
        except Exception:
            continue
        wheels.append((canonicalize_name(name), str(version), tags))

    missing: dict[str, list[str]] = {}
    for task_id in suite["task_ids"]:
        lock_path = task_root / task_id / "requirements.lock"
        for raw in lock_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            requirement = Requirement(line)
            found = any(
                name == canonicalize_name(requirement.name)
                and requirement.specifier.contains(version)
                and compatible(tags, args.python_version)
                for name, version, tags in wheels
            )
            if not found:
                missing.setdefault(task_id, []).append(line)
    for task_id, requirements in missing.items():
        print(f"MISSING {task_id}: {', '.join(requirements)}")
    print(
        f"Python-{args.python_version} wheel coverage: "
        f"{suite['task_count'] - len(missing)}/{suite['task_count']} tasks"
    )
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
