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

from featureliftbench.suite_utils import detect_eval_flake
from featureliftbench.suite_utils import functional_gate_value
from featureliftbench.suite_utils import resolve_suite_artifact_path
from featureliftbench.closure_gold import load_closure_gold, score_closure
from featureliftbench.trajectory_audit import audit_trajectory, read_event_jsonl


def aggregate_suite_summaries(suite_dirs: list[Path]) -> dict[str, Any]:
    summaries: list[dict[str, Any]] = []
    for suite_dir in suite_dirs:
        suite_path = suite_dir / "suite.json"
        if not suite_path.is_file():
            raise FileNotFoundError(f"missing suite.json: {suite_path}")
        suite = load_json(suite_path)
        summary = suite.get("summary") if isinstance(suite.get("summary"), dict) else {}
        runs = [run for run in suite.get("runs") or [] if isinstance(run, dict)]
        functional_values = [functional_gate_value(run) for run in runs]
        functional_passed = summary.get("functional_passed")
        if not isinstance(functional_passed, int):
            functional_passed = sum(value == 1.0 for value in functional_values)
        total = summary.get("total", len(runs))
        summaries.append(
            {
                "suite_dir": str(suite_dir),
                "suite_name": suite_dir.name,
                "passed": summary.get("passed", 0),
                "functional_passed": functional_passed,
                "total": total,
                "missing_submissions": summary.get("missing_submissions", 0),
                "recovered_submissions": summary.get("recovered_submissions", 0),
                "average_final_score": summary.get("average_final_score", 0.0),
            }
        )

    def _mean_std(key: str) -> dict[str, float]:
        values = [float(item[key]) for item in summaries]
        if not values:
            return {"mean": 0.0, "std": 0.0}
        mean = sum(values) / len(values)
        if len(values) == 1:
            return {"mean": round(mean, 6), "std": 0.0}
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        return {"mean": round(mean, 6), "std": round(variance**0.5, 6)}

    pass_rates = [
        (item["passed"] / item["total"]) if item["total"] else 0.0 for item in summaries
    ]
    functional_pass_rates = [
        (item["functional_passed"] / item["total"]) if item["total"] else 0.0
        for item in summaries
    ]
    pass_rate_mean = sum(pass_rates) / len(pass_rates) if pass_rates else 0.0
    if len(pass_rates) > 1:
        pass_rate_std = (
            sum((value - pass_rate_mean) ** 2 for value in pass_rates) / len(pass_rates)
        ) ** 0.5
    else:
        pass_rate_std = 0.0
    functional_pass_rate_mean = (
        sum(functional_pass_rates) / len(functional_pass_rates)
        if functional_pass_rates
        else 0.0
    )
    functional_pass_rate_std = (
        (
            sum(
                (value - functional_pass_rate_mean) ** 2
                for value in functional_pass_rates
            )
            / len(functional_pass_rates)
        )
        ** 0.5
        if len(functional_pass_rates) > 1
        else 0.0
    )

    return {
        "run_count": len(summaries),
        "suites": summaries,
        "passed": _mean_std("passed"),
        "functional_passed": _mean_std("functional_passed"),
        "missing_submissions": _mean_std("missing_submissions"),
        "recovered_submissions": _mean_std("recovered_submissions"),
        "average_final_score": _mean_std("average_final_score"),
        "pass_rate": {
            "mean": round(pass_rate_mean, 6),
            "std": round(pass_rate_std, 6),
        },
        "functional_pass_rate": {
            "mean": round(functional_pass_rate_mean, 6),
            "std": round(functional_pass_rate_std, 6),
        },
    }


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def enrich_run(run: dict[str, Any], suite_dir: Path) -> dict[str, Any]:
    task_id = run.get("task_id", "")
    run_json_path = resolve_suite_artifact_path(
        suite_dir,
        task_id,
        "run.json",
        run.get("run_json"),
    )
    if not run_json_path.is_file():
        return dict(run)

    detail = load_json(run_json_path)
    agent = detail.get("agent") or {}
    usage = agent.get("usage") or {}
    evaluation = detail.get("evaluation") or {}
    submission = detail.get("submission") or {}
    scores = evaluation.get("scores") or {}
    metrics = evaluation.get("metrics") or {}

    result_json_path = resolve_suite_artifact_path(
        suite_dir,
        task_id,
        "eval/result.json",
        evaluation.get("result_json") or run.get("result_json"),
    )
    if result_json_path.is_file():
        eval_detail = load_json(result_json_path)
        scores = eval_detail.get("scores") or scores
        metrics = eval_detail.get("metrics") or metrics
        build_pass = eval_detail.get("build_pass", evaluation.get("build_pass"))
        test_pass = eval_detail.get("test_pass", evaluation.get("test_pass"))
    else:
        eval_detail = {}
        build_pass = evaluation.get("build_pass")
        test_pass = evaluation.get("test_pass")

    task_run_dir = suite_dir / task_id
    eval_flake = detect_eval_flake(task_run_dir)
    graph_usage = detail.get("repo_graph") if isinstance(detail.get("repo_graph"), dict) else {}
    graph_build_path = task_run_dir / "agent" / "repo_graph_build.json"
    graph_build = load_json(graph_build_path) if graph_build_path.is_file() else {}
    events_path = task_run_dir / "agent" / "openhands_events.jsonl"
    trajectory = audit_trajectory(read_event_jsonl(events_path))
    closure_gold_score = _closure_gold_score(task_run_dir, task_id)

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
            "submission_recovered": submission.get("recovered", False),
            "submission_recovery_sources": submission.get("recovery_sources", []),
            "trajectory_json": str(suite_dir / task_id / "agent" / "trajectory.json"),
            "trajectory_audit": trajectory,
            "public_pass": _gate_pass(eval_detail, "public_tests"),
            "hidden_pass": _gate_pass(eval_detail, "hidden_tests"),
            "install_pass": _gate_pass(eval_detail, "submission_install"),
            "context_audit": usage.get("context_audit", {}),
            "repo_graph": {
                **graph_usage,
                "build_duration_seconds": graph_build.get("duration_seconds"),
                "cache_hit": (graph_build.get("cache") or {}).get("hit")
                if isinstance(graph_build.get("cache"), dict)
                else None,
                "graph_bytes": graph_build.get("graph_bytes"),
                "rss_peak_bytes": graph_build.get("rss_peak_bytes"),
                "closure_gold_file_score": closure_gold_score,
            }
            if graph_usage or graph_build
            else {},
            "system_fingerprints": trajectory.get("system_fingerprints", []),
            "status": evaluation.get("status") or run.get("status"),
            "eval_flake": eval_flake,
        }
    )
    return enriched


def _gate_pass(evaluation: dict[str, Any], key: str) -> bool | None:
    gate = evaluation.get(key)
    return gate.get("passed") if isinstance(gate, dict) and isinstance(gate.get("passed"), bool) else None


def _closure_gold_score(task_run_dir: Path, task_id: str) -> dict[str, Any] | None:
    task_dir = _REPO_ROOT / "benchmark" / "tasks" / task_id
    closure_path = task_run_dir / "agent" / "state" / "repo_graph" / "closure_overlay.json"
    if not task_dir.is_dir() or not closure_path.is_file():
        return None
    closure = load_json(closure_path)
    predictions: list[str] = []
    for node in closure.get("candidate_nodes", []):
        if not isinstance(node, dict):
            continue
        location = node.get("location")
        if not isinstance(location, str) or not location:
            continue
        path = location.rsplit(":", 1)[0]
        predictions.append(path if path.startswith("repo/") else f"repo/{path}")
    score = score_closure(load_closure_gold(task_dir), predictions, kind="file")
    return score.as_dict() if score is not None else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "suite_dir",
        type=Path,
        nargs="?",
        default=None,
        help="Directory containing suite.json from run-agent",
    )
    parser.add_argument(
        "--aggregate",
        nargs="+",
        type=Path,
        help="Aggregate multiple suite directories (mean/std over summary fields)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="suite-comparison.json path (default: <suite-parent>/<suite>-comparison.json)",
    )
    parser.add_argument(
        "--analysis-prefix",
        type=Path,
        default=None,
        help="Analysis output prefix without suffix (default: <suite-parent>/<suite>-analysis)",
    )
    args = parser.parse_args()

    if args.aggregate:
        aggregate_dirs = [path.resolve() for path in args.aggregate]
        aggregate = aggregate_suite_summaries(aggregate_dirs)
        aggregate_path = args.output or aggregate_dirs[0].parent / "suite-aggregate.json"
        aggregate_path.parent.mkdir(parents=True, exist_ok=True)
        with aggregate_path.open("w", encoding="utf-8") as handle:
            json.dump(
                {
                    "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                    **aggregate,
                },
                handle,
                ensure_ascii=False,
                indent=2,
            )
            handle.write("\n")
        print(f"Wrote {aggregate_path}")
        print(
            "functional_pass_rate mean={mean} std={std} | "
            "workflow_pass_rate mean={workflow_mean} | "
            "recovered_submissions mean={rec_mean}".format(
                mean=aggregate["functional_pass_rate"]["mean"],
                std=aggregate["functional_pass_rate"]["std"],
                workflow_mean=aggregate["pass_rate"]["mean"],
                rec_mean=aggregate["recovered_submissions"]["mean"],
            )
        )
        return 0

    if args.suite_dir is None:
        raise SystemExit("suite_dir is required unless --aggregate is used")

    suite_dir = args.suite_dir.resolve()
    suite_path = suite_dir / "suite.json"
    if not suite_path.is_file():
        raise SystemExit(f"missing suite.json: {suite_path}")

    suite = load_json(suite_path)
    suite_name = suite_dir.name
    runs = [enrich_run(run, suite_dir) for run in suite.get("runs") or []]
    eval_flake_count = sum(1 for run in runs if run.get("eval_flake"))

    comparison_path = args.output or suite_dir.parent / f"{suite_name}-comparison.json"
    analysis_prefix = args.analysis_prefix or suite_dir.parent / f"{suite_name}-analysis"

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
