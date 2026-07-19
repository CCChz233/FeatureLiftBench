#!/usr/bin/env python3
"""Run the 62 historical infra-failure submissions into immutable new suites."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "artifacts/research_analysis/v1_1/infra_reeval_manifest.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("freeze_manifest", type=Path)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def main() -> int:
    args = parse_args()
    freeze = load(args.freeze_manifest)
    manifest = load(args.manifest)
    output_root = args.output_root.resolve()
    results = []
    for suite in manifest["suites"]:
        source = ROOT / suite["source_suite"]
        destination = output_root / suite["output_suffix"]
        command = [
            sys.executable,
            str(ROOT / "harness/scripts/reeval_suite.py"),
            str(source),
            "--output-dir", str(destination),
            "--workers", str(max(1, args.workers)),
            "--docker",
            "--docker-image", str(freeze["docker"]["immutable_ref"]),
        ]
        for task_id in suite["task_ids"]:
            command.extend(["--task-id", task_id])
        if args.dry_run:
            command.append("--dry-run")
        completed = subprocess.run(command, cwd=ROOT, text=True, check=False)
        results.append({
            "source_suite": suite["source_suite"],
            "output_suite": destination.relative_to(ROOT).as_posix(),
            "task_count": len(suite["task_ids"]),
            "returncode": completed.returncode,
        })
        if completed.returncode != 0:
            raise RuntimeError(f"immutable re-evaluation failed for {source}")

    evaluator_status = {"passed": 0, "failed": 0, "missing": 0}
    task_rows = []
    if not args.dry_run:
        for suite in manifest["suites"]:
            destination = output_root / suite["output_suffix"]
            for task_id in suite["task_ids"]:
                result_path = destination / task_id / "eval/result.json"
                if result_path.is_file():
                    result = load(result_path)
                    status = str(result.get("status") or "failed")
                else:
                    status = "missing"
                evaluator_status[status if status in evaluator_status else "failed"] += 1
                task_rows.append({
                    "task_id": task_id,
                    "source_suite": suite["source_suite"],
                    "output_result": result_path.relative_to(ROOT).as_posix(),
                    "evaluation_status": status,
                })
    payload = {
        "schema_version": "featureliftbench.infra_reevaluation_summary.v1",
        "freeze_id": freeze["freeze_id"],
        "docker_image_id": freeze["docker"]["image_id"],
        "docker_immutable_ref": freeze["docker"]["immutable_ref"],
        "source_run_count": manifest["run_count"],
        "suite_count": len(results),
        "dry_run": args.dry_run,
        "suite_results": results,
        "evaluation_status_counts": evaluator_status,
        "rows": task_rows,
        "interpretation": (
            "Evaluation failures here are current submission/task outcomes. The key infrastructure check is "
            "that every selected historical submission receives a complete new result under the frozen image."
        ),
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "source_run_count": payload["source_run_count"],
        "suite_count": payload["suite_count"],
        "evaluation_status_counts": evaluator_status,
        "output_root": output_root.relative_to(ROOT).as_posix(),
    }, indent=2, sort_keys=True))
    return 0 if args.dry_run or evaluator_status["missing"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
