#!/usr/bin/env python3
"""Build the code-free Python-150 compactness reference registry."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "harness"
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))

from featureliftbench.freeze import file_manifest, manifest_digest
from featureliftbench.metrics import count_files, count_python_loc


DEFAULT_OUTPUT = ROOT / "benchmark" / "references" / "compactness.json"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def _tree_digest(path: Path) -> str:
    return manifest_digest({"files": file_manifest([path], root=path)})


def build_payload() -> dict[str, Any]:
    task_dirs = sorted(
        path
        for path in (ROOT / "benchmark" / "tasks").iterdir()
        if path.is_dir() and (path / "metadata.json").is_file()
    )
    if len(task_dirs) != 150:
        raise ValueError(f"expected 150 Python tasks, found {len(task_dirs)}")
    tasks: dict[str, dict[str, Any]] = {}
    for task_dir in task_dirs:
        task_id = task_dir.name
        oracle = ROOT / "benchmark" / "submissions" / task_id / "oracle"
        if not oracle.is_dir():
            raise ValueError(f"{task_id}: local Oracle submission is missing")
        tasks[task_id] = {
            "python_loc": count_python_loc(oracle),
            "file_count": count_files(oracle),
            "reference_tree_sha256": _tree_digest(oracle),
        }
    payload: dict[str, Any] = {
        "schema_version": "featureliftbench.compactness_reference.v1",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "task_count": len(tasks),
        "reference_kind": "frozen_oracle_measurements_without_source_code",
        "tasks": tasks,
    }
    payload["registry_id"] = manifest_digest(payload)
    return payload


def _comparable(payload: dict[str, Any]) -> dict[str, Any]:
    result = dict(payload)
    result.pop("generated_at", None)
    return result


def main() -> int:
    args = _parse_args()
    payload = build_payload()
    output = args.output.resolve()
    if args.check:
        tracked = json.loads(output.read_text(encoding="utf-8"))
        if _comparable(tracked) != _comparable(payload):
            raise ValueError("tracked compactness registry differs from local Oracles")
        print(
            f"Verified compactness reference registry: "
            f"{payload['task_count']} tasks, {payload['registry_id']}"
        )
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(
        f"Wrote compactness reference registry: "
        f"{payload['task_count']} tasks, {payload['registry_id']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
