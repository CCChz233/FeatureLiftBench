#!/usr/bin/env python3
"""Build or verify the code-free Python-200-prime compactness registry."""

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

from featureliftbench.freeze import file_manifest, manifest_digest  # noqa: E402
from featureliftbench.metrics import count_files, count_python_loc  # noqa: E402


DEFAULT_OUTPUT = ROOT / "benchmark" / "references" / "python200_prime_compactness.json"
SUITE_PATH = ROOT / "benchmark" / "selection" / "python200_hard_suite.json"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def _tree_digest(path: Path) -> str:
    resolved = path.resolve()
    return manifest_digest({"files": file_manifest([resolved], root=resolved)})


def _reference(task_id: str) -> tuple[Path, str]:
    baseline = ROOT / "benchmark" / "submissions" / task_id / "oracle"
    if baseline.is_dir():
        return baseline, "python150_oracle"
    hard50 = ROOT / "benchmark" / "hard50_pilot" / task_id / "reference_solution"
    if hard50.is_dir():
        return hard50, "hard50_reference_solution"
    raise ValueError(f"{task_id}: reference solution missing")


def build_payload() -> dict[str, Any]:
    suite = json.loads(SUITE_PATH.read_text(encoding="utf-8"))
    task_ids = suite.get("task_ids")
    if not isinstance(task_ids, list) or len(task_ids) != 200:
        raise ValueError("expected a 200-task suite")
    tasks: dict[str, dict[str, Any]] = {}
    kinds: dict[str, int] = {}
    for task_id in sorted(task_ids):
        reference, kind = _reference(task_id)
        kinds[kind] = kinds.get(kind, 0) + 1
        tasks[task_id] = {
            "python_loc": count_python_loc(reference),
            "file_count": count_files(reference),
            "reference_tree_sha256": _tree_digest(reference),
            "reference_kind": kind,
        }
    if kinds != {"python150_oracle": 150, "hard50_reference_solution": 50}:
        raise ValueError(f"unexpected reference composition: {kinds}")
    payload: dict[str, Any] = {
        "schema_version": "featureliftbench.compactness_reference.v1",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "suite_id": suite.get("suite_id"),
        "task_count": len(tasks),
        "reference_kind": "frozen_python200_prime_reference_measurements_without_source_code",
        "reference_composition": kinds,
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
            raise ValueError("tracked Python-200-prime compactness registry drifted")
        print(f"Verified Python-200-prime compactness registry: {payload['registry_id']}")
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote Python-200-prime compactness registry: {payload['registry_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
