#!/usr/bin/env python3
"""Classify and audit the immutable re-evaluation of 62 historical infra failures."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "artifacts/research_analysis/v1_1/infra_reeval_manifest.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_root", type=Path)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    return parser.parse_args()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def classify(result: dict[str, Any]) -> str:
    sandbox = result.get("sandbox") if isinstance(result.get("sandbox"), dict) else {}
    if sandbox.get("docker_sandbox_error") is True:
        return "environment"
    for key in ("dependency_install", "eval_tooling", "submission_install"):
        value = result.get(key) if isinstance(result.get(key), dict) else {}
        if value.get("timed_out") is True:
            return "timeout"
        if value.get("skipped") is not True and value.get("passed") is False:
            return "dependency" if key == "dependency_install" else "environment"
    for key in ("build", "public_tests", "hidden_tests"):
        value = result.get(key) if isinstance(result.get(key), dict) else {}
        if value.get("timed_out") is True:
            return "timeout"
    return "passed" if result.get("status") == "passed" else "functional_failure"


def main() -> int:
    args = parse_args()
    run_root = args.run_root.resolve()
    manifest = load(args.manifest)
    rows = []
    classes = Counter()
    incomplete_schema = []
    required_keys = {
        "status", "build_pass", "test_pass", "original_import_pass", "dependency_install",
        "eval_tooling", "build", "public_tests", "hidden_tests", "metrics", "scores",
    }
    for suite in manifest["suites"]:
        for task_id in suite["task_ids"]:
            path = run_root / suite["output_suffix"] / task_id / "eval/result.json"
            if not path.is_file():
                classes["missing"] += 1
                rows.append({"task_id": task_id, "result_path": path.relative_to(ROOT).as_posix(), "classification": "missing"})
                continue
            result = load(path)
            missing_keys = sorted(required_keys - set(result))
            if missing_keys:
                incomplete_schema.append(task_id)
            classification = classify(result)
            classes[classification] += 1
            rows.append({
                "task_id": task_id,
                "source_suite": suite["source_suite"],
                "result_path": path.relative_to(ROOT).as_posix(),
                "classification": classification,
                "status": result.get("status"),
                "missing_schema_keys": missing_keys,
            })
    infra_count = sum(classes[key] for key in ("dependency", "environment", "timeout"))
    payload = {
        "schema_version": "featureliftbench.infra_reevaluation_analysis.v1",
        "source_run_count": manifest["run_count"],
        "new_result_count": len(rows) - classes["missing"],
        "classification_counts": dict(sorted(classes.items())),
        "new_infrastructure_failure_count": infra_count,
        "incomplete_result_schema_count": len(incomplete_schema),
        "incomplete_result_schema_task_ids": sorted(incomplete_schema),
        "gate_pass": (
            len(rows) == manifest["run_count"]
            and classes["missing"] == 0
            and infra_count == 0
            and not incomplete_schema
        ),
        "rows": rows,
        "interpretation": (
            "functional_failure means the archived Agent submission or a quarantined task failed current "
            "functional evaluation; it is distinct from dependency/environment/timeout noise."
        ),
    }
    output = run_root / "analysis.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in (
        "source_run_count", "new_result_count", "classification_counts",
        "new_infrastructure_failure_count", "incomplete_result_schema_count", "gate_pass",
    )}, indent=2, sort_keys=True))
    return 0 if payload["gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
