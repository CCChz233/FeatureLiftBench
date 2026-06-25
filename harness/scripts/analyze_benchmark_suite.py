#!/usr/bin/env python3
"""Build suite-comparison.json from a run-agent suite and render analysis reports."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "harness"))

from featureliftbench.paths import EXPERIMENTS_DIR
from featureliftbench.suite_utils import detect_eval_flake


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def enrich_run(run: dict[str, Any], suite_dir: Path) -> dict[str, Any]:
    task_id = run.get("task_id", "")
    run_json_path = Path(run.get("run_json") or suite_dir / task_id / "run.json")
    if not run_json_path.is_file():
        return dict(run)

    detail = load_json(run_json_path)
    agent = detail.get("agent") or {}
    usage = agent.get("usage") or {}
    evaluation = detail.get("evaluation") or {}
    scores = evaluation.get("scores") or {}
    metrics = evaluation.get("metrics") or {}

    result_json_path = Path(evaluation.get("result_json") or suite_dir / task_id / "eval" / "result.json")
    if result_json_path.is_file():
        eval_detail = load_json(result_json_path)
        scores = eval_detail.get("scores") or scores
        metrics = eval_detail.get("metrics") or metrics
        build_pass = eval_detail.get("build_pass", evaluation.get("build_pass"))
        test_pass = eval_detail.get("test_pass", evaluation.get("test_pass"))
    else:
        build_pass = evaluation.get("build_pass")
        test_pass = evaluation.get("test_pass")

    task_run_dir = suite_dir / task_id
    eval_flake = detect_eval_flake(task_run_dir)

    enriched = dict(run)
    enriched.update(
        {
            "functional_gate": scores.get("functional_gate"),
            "extraction_ratio": scores.get("extraction_ratio"),
            "final_score": scores.get("final_score", run.get("final_score")),
            "build_pass": build_pass,
            "test_pass": test_pass,
            "submission_loc": metrics.get("loc"),
            "source_loc": metrics.get("source_loc"),
            "assistant_steps": usage.get("assistant_steps"),
            "api_calls": usage.get("api_calls"),
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "total_tokens": usage.get("total_tokens"),
            "agent_duration_seconds": agent.get("duration_seconds"),
            "trajectory_json": str(suite_dir / task_id / "agent" / "trajectory.json"),
            "status": evaluation.get("status") or run.get("status"),
            "eval_flake": eval_flake,
        }
    )
    return enriched


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "suite_dir",
        type=Path,
        help="Directory containing suite.json from run-agent",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="suite-comparison.json path (default: experiments/mini-swe-agent/<suite>-comparison.json)",
    )
    parser.add_argument(
        "--analysis-prefix",
        type=Path,
        default=None,
        help="Analysis output prefix without suffix (default: experiments/mini-swe-agent/<suite>-analysis)",
    )
    args = parser.parse_args()

    suite_dir = args.suite_dir.resolve()
    suite_path = suite_dir / "suite.json"
    if not suite_path.is_file():
        raise SystemExit(f"missing suite.json: {suite_path}")

    suite = load_json(suite_path)
    suite_name = suite_dir.name
    runs = [enrich_run(run, suite_dir) for run in suite.get("runs") or []]
    eval_flake_count = sum(1 for run in runs if run.get("eval_flake"))

    comparison_path = args.output or EXPERIMENTS_DIR / "mini-swe-agent" / f"{suite_name}-comparison.json"
    analysis_prefix = args.analysis_prefix or EXPERIMENTS_DIR / "mini-swe-agent" / f"{suite_name}-analysis"

    comparison = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "eval_flake_count": eval_flake_count,
        "suites": {
            suite_name: {
                **{k: v for k, v in suite.items() if k != "runs"},
                "eval_flake_count": eval_flake_count,
                "runs": runs,
            }
        },
    }

    comparison_path.parent.mkdir(parents=True, exist_ok=True)
    with comparison_path.open("w", encoding="utf-8") as handle:
        json.dump(comparison, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    print(f"Wrote {comparison_path}")

    analyze_script = Path(__file__).resolve().parent / "analyze_suite_results.py"
    subprocess.run(
        [
            sys.executable,
            str(analyze_script),
            "--input",
            str(comparison_path),
            "--output-prefix",
            str(analysis_prefix),
        ],
        check=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
