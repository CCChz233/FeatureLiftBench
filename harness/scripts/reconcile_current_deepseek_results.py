#!/usr/bin/env python3
"""Reconcile current DeepSeek Main vs Lite V1 (main-budget) result artifacts.

The compared Lite V1 runs use the frozen Lite V1 protocol with Main's 120-step
budget. They are not the 45+10 frozen envelope. Live experiment directories
are the primary evidence; incomplete results packs are not required.

The output follows the current FeatureLiftBench metric contract:

* Functional Pass Rate is the correctness headline.
* Reference-Relative Extraction Size (RRES) is reported only for
  functionally passing submissions with trusted compactness metrics.
* Functional failures use one mutually exclusive primary stage.
* Historical workflow ``summary.passed`` is retained only as an operational
  field and is never used as Functional Pass.

This script is deliberately read-only with respect to benchmark tasks and raw
experiment archives.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_API_MAIN150_DIR = (
    REPO_ROOT
    / "experiments/FeatureLiftBench-v3-846-20260801-ready/experiments/export"
    / "FeatureLiftBench-deepseek-v4-flash-150-20260805/deepseek-v4-flash-0731"
)
DEFAULT_API_EXTERNAL50_DIR = (
    REPO_ROOT
    / "experiments/python/openhands/deepseek-v4-flash"
    / "external50-deepseek-v4-flash-0805-main-001"
)
DEFAULT_API_LITE_DIR = (
    REPO_ROOT
    / "experiments/python/openhands/deepseek-v4-flash"
    / "python200-deepseek-v4-flash-lite-v1-main-budget-0812-002"
)
DEFAULT_LOCAL_MAIN_DIR = (
    REPO_ROOT
    / "experiments/python/openhands/deepseek-v4-flash"
    / "python200-deepseek-v4-flash-vllm-local-0812-001"
)
DEFAULT_LOCAL_LITE_DIR = (
    REPO_ROOT
    / "experiments/python/openhands/deepseek-v4-flash"
    / "python200-deepseek-v4-flash-lite-v1-vllm-local-0813-001"
)
DEFAULT_OUTPUT = (
    REPO_ROOT
    / "artifacts/research_analysis/current_results/deepseek_main_vs_lite_v1_20260817.json"
)


def _suite_index(suite: dict[str, Any], expected: int) -> dict[str, dict[str, Any]]:
    runs = suite.get("runs")
    if not isinstance(runs, list):
        raise TypeError("suite.runs must be a list")
    index: dict[str, dict[str, Any]] = {}
    for run in runs:
        if not isinstance(run, dict) or not isinstance(run.get("task_id"), str):
            raise TypeError("every suite row must have a string task_id")
        task_id = run["task_id"]
        if task_id in index:
            raise ValueError(f"duplicate task_id: {task_id}")
        score = run.get("final_score")
        if score not in {0, 0.0, 1, 1.0}:
            raise ValueError(f"non-binary compact final_score for {task_id}: {score!r}")
        index[task_id] = run
    if len(index) != expected:
        raise ValueError(f"expected {expected} unique suite rows, found {len(index)}")
    return index


def _functional_pass(run: dict[str, Any]) -> bool:
    return run.get("final_score") == 1.0


def _gate_value(result: dict[str, Any], direct: str, nested: str) -> bool | None:
    value = result.get(direct)
    if isinstance(value, bool):
        return value
    value = result.get(nested)
    if isinstance(value, dict) and isinstance(value.get("passed"), bool):
        return value["passed"]
    return None


def _primary_failure_stage(result: dict[str, Any]) -> str:
    build = _gate_value(result, "build_pass", "build")
    public = _gate_value(result, "public_tests_pass", "public_tests")
    hidden = _gate_value(result, "hidden_tests_pass", "hidden_tests")
    isolation = _gate_value(result, "isolation_pass", "isolation")
    score = (result.get("scores") or {}).get("functional_gate")
    eval_tooling = result.get("eval_tooling") or {}
    sandbox = result.get("sandbox") or {}

    if eval_tooling.get("passed") is False or sandbox.get("docker_sandbox_error") is True:
        return "evaluator_infra"
    if build is False:
        return "build_failure"
    if public is False:
        return "public_failure"
    if hidden is False:
        return "hidden_failure"
    if isolation is False:
        return "isolation_failure"
    if score == 1.0:
        return "functional_pass"
    return "unknown"


def _quantile(values: list[float], probability: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def _rres_summary(values: list[float], functional_passed: int) -> dict[str, Any]:
    return {
        "metric": "reference_relative_extraction_size",
        "direction": "lower_is_better",
        "eligible_functional_passes": functional_passed,
        "available": len(values),
        "coverage": round(len(values) / functional_passed, 6) if functional_passed else 0.0,
        "median": round(statistics.median(values), 6) if values else None,
        "q1": round(_quantile(values, 0.25), 6) if values else None,
        "q3": round(_quantile(values, 0.75), 6) if values else None,
        "minimum": round(min(values), 6) if values else None,
        "maximum": round(max(values), 6) if values else None,
    }


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def _load_detailed_results_dir(suite_dir: Path) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for path in sorted(suite_dir.glob("*/eval/result.json")):
        result = _load_json(path)
        task_id = result.get("task_id")
        if not isinstance(task_id, str):
            raise TypeError(f"eval result missing task_id: {path}")
        if task_id in results:
            raise ValueError(f"duplicate eval result for {task_id}")
        results[task_id] = result
    return results


def _rel(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(REPO_ROOT))
    except ValueError:
        return str(resolved)


def _source_entry(path: Path) -> dict[str, str]:
    return {"path": _rel(path)}


def _rres_ratio(result: dict[str, Any]) -> float | None:
    ratio = (result.get("scores") or {}).get("reference_relative_loc_ratio")
    if isinstance(ratio, (int, float)) and not isinstance(ratio, bool):
        return float(ratio)
    return None


def _summarize_detailed_suite(
    suite: dict[str, Any],
    results: dict[str, dict[str, Any]],
    expected: int,
) -> dict[str, Any]:
    index = _suite_index(suite, expected)
    categories: Counter[str] = Counter()
    task_ids_by_category: dict[str, list[str]] = {}
    rres_values: list[float] = []

    for task_id, run in index.items():
        if _functional_pass(run):
            expected_category = "functional_pass"
        elif run.get("status") == "missing_submission":
            expected_category = "missing_submission"
        else:
            expected_category = None

        result = results.get(task_id)
        if result is None:
            category = expected_category or "stage_evidence_unavailable"
        else:
            category = _primary_failure_stage(result)
            result_gate = (result.get("scores") or {}).get("functional_gate")
            if result_gate != run.get("final_score"):
                raise ValueError(
                    f"suite/evaluator functional mismatch for {task_id}: "
                    f"{run.get('final_score')} vs {result_gate}"
                )
            if result_gate == 1.0:
                ratio = (result.get("scores") or {}).get(
                    "reference_relative_loc_ratio"
                )
                if isinstance(ratio, (int, float)) and not isinstance(ratio, bool):
                    rres_values.append(float(ratio))

        categories[category] += 1
        task_ids_by_category.setdefault(category, []).append(task_id)

    for task_ids in task_ids_by_category.values():
        task_ids.sort()
    functional_passed = sum(_functional_pass(run) for run in index.values())
    return {
        "assigned": expected,
        "functional_passed": functional_passed,
        "functional_pass_rate": round(functional_passed / expected, 6),
        "run_status_passed": sum(run.get("status") == "passed" for run in index.values()),
        "eval_result_coverage": len(results),
        "primary_outcomes": dict(sorted(categories.items())),
        "task_ids_by_primary_outcome": dict(sorted(task_ids_by_category.items())),
        "rres": _rres_summary(rres_values, functional_passed),
    }


def _delta_summary(values: list[float]) -> dict[str, Any]:
    if not values:
        return {
            "available": 0,
            "median": None,
            "q1": None,
            "q3": None,
            "lite_smaller": 0,
            "equal": 0,
            "lite_larger": 0,
        }
    return {
        "available": len(values),
        "median": round(statistics.median(values), 6),
        "q1": round(_quantile(values, 0.25), 6),
        "q3": round(_quantile(values, 0.75), 6),
        "lite_smaller": sum(value < 0 for value in values),
        "equal": sum(abs(value) < 1e-12 for value in values),
        "lite_larger": sum(value > 0 for value in values),
    }


def _paired_rres(
    main_suite: dict[str, Any],
    lite_suite: dict[str, Any],
    main_results: dict[str, dict[str, Any]],
    lite_results: dict[str, dict[str, Any]],
    task_ids: set[str],
) -> dict[str, Any]:
    matrix = _paired_matrix(main_suite, lite_suite, task_ids)
    main = {run["task_id"]: _functional_pass(run) for run in main_suite["runs"]}
    lite = {run["task_id"]: _functional_pass(run) for run in lite_suite["runs"]}
    both_pass = [
        task_id
        for task_id in sorted(task_ids)
        if main[task_id] and lite[task_id]
    ]
    main_values: list[float] = []
    lite_values: list[float] = []
    deltas: list[float] = []
    for task_id in both_pass:
        main_ratio = _rres_ratio(main_results.get(task_id) or {})
        lite_ratio = _rres_ratio(lite_results.get(task_id) or {})
        if main_ratio is None or lite_ratio is None:
            continue
        main_values.append(main_ratio)
        lite_values.append(lite_ratio)
        deltas.append(lite_ratio - main_ratio)
    return {
        **matrix,
        "paired_rres_available": len(main_values),
        "main": _rres_summary(main_values, len(main_values)),
        "lite_v1": _rres_summary(lite_values, len(lite_values)),
        "delta_lite_minus_main": _delta_summary(deltas),
    }


def _usage(suite: dict[str, Any], task_ids: set[str] | None = None) -> dict[str, int]:
    keys = ("total_tokens", "prompt_tokens", "completion_tokens", "api_calls", "assistant_steps")
    totals = {key: 0 for key in keys}
    for run in suite.get("runs") or []:
        if task_ids is not None and run.get("task_id") not in task_ids:
            continue
        usage = run.get("agent_usage") or {}
        for key in keys:
            value = usage.get(key)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                totals[key] += int(value)
    return totals


def _paired_matrix(
    main_suite: dict[str, Any], lite_suite: dict[str, Any], task_ids: set[str]
) -> dict[str, int]:
    main = {run["task_id"]: _functional_pass(run) for run in main_suite["runs"]}
    lite = {run["task_id"]: _functional_pass(run) for run in lite_suite["runs"]}
    if not task_ids <= main.keys() or not task_ids <= lite.keys():
        raise ValueError("paired matrix task IDs are not covered by both suites")
    counts = Counter((main[task_id], lite[task_id]) for task_id in task_ids)
    return {
        "both_pass": counts[(True, True)],
        "main_only_pass": counts[(True, False)],
        "lite_only_pass": counts[(False, True)],
        "both_fail": counts[(False, False)],
    }


def _split_counts(index: dict[str, dict[str, Any]], task_ids: set[str]) -> int:
    return sum(_functional_pass(index[task_id]) for task_id in task_ids)


def build_report(
    api_main150_dir: Path,
    api_external50_dir: Path,
    api_lite_dir: Path,
    local_main_dir: Path,
    local_lite_dir: Path,
) -> dict[str, Any]:
    main_ids = {
        path.name
        for path in (REPO_ROOT / "benchmark/tasks").iterdir()
        if (path / "metadata.json").is_file()
    }
    external_ids = {
        path.name
        for path in (REPO_ROOT / "benchmark/external50").iterdir()
        if (path / "metadata.json").is_file()
    }
    if len(main_ids) != 150 or len(external_ids) != 50 or main_ids & external_ids:
        raise ValueError("expected disjoint Main-150 and External-50 task manifests")

    api_main150 = _load_json(api_main150_dir / "suite.json")
    api_external50 = _load_json(api_external50_dir / "suite.json")
    api_lite = _load_json(api_lite_dir / "suite.json")
    local_main = _load_json(local_main_dir / "suite.json")
    local_lite = _load_json(local_lite_dir / "suite.json")
    api_main150_results = _load_detailed_results_dir(api_main150_dir)
    api_external50_results = _load_detailed_results_dir(api_external50_dir)
    api_lite_results = _load_detailed_results_dir(api_lite_dir)
    local_main_results = _load_detailed_results_dir(local_main_dir)
    local_lite_results = _load_detailed_results_dir(local_lite_dir)

    api_main = {
        "runs": list(api_main150["runs"]) + list(api_external50["runs"]),
    }
    api_main_results = {**api_main150_results, **api_external50_results}

    api_main150_summary = _summarize_detailed_suite(
        api_main150, api_main150_results, 150
    )
    api_main_summary = _summarize_detailed_suite(api_main, api_main_results, 200)
    api_lite_summary = _summarize_detailed_suite(api_lite, api_lite_results, 200)
    local_main_summary = _summarize_detailed_suite(
        local_main, local_main_results, 200
    )
    local_lite_summary = _summarize_detailed_suite(
        local_lite, local_lite_results, 200
    )

    api_lite_index = _suite_index(api_lite, 200)
    local_main_index = _suite_index(local_main, 200)
    local_lite_index = _suite_index(local_lite, 200)
    python200_ids = main_ids | external_ids

    return {
        "schema_version": "featureliftbench.current_result_reconciliation.v2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "method_compared": {
            "name": "lite_v1_main_budget",
            "protocol": "contract_closure_gate_lite_v1",
            "budget": "main_120_step_plus_repair",
            "not": "frozen_45_plus_10_envelope",
        },
        "metric_contract": {
            "primary": "functional_pass_rate",
            "secondary": "reference_relative_extraction_size",
            "functional_pass": "build AND public AND hidden AND isolation",
            "rres": "submission_normalized_loc / frozen_reference_normalized_loc",
            "rres_population": "functionally passing submissions only",
            "primary_failure_precedence": [
                "missing_submission",
                "build_failure",
                "public_failure",
                "hidden_failure",
                "isolation_failure",
                "functional_pass",
            ],
        },
        "sources": {
            "api_main150_dir": _source_entry(api_main150_dir),
            "api_external50_dir": _source_entry(api_external50_dir),
            "api_lite_dir": _source_entry(api_lite_dir),
            "local_main_dir": _source_entry(local_main_dir),
            "local_lite_dir": _source_entry(local_lite_dir),
        },
        "headline": {
            "api": {
                "main": api_main_summary,
                "lite_v1": api_lite_summary,
                "lite_delta_passes": api_lite_summary["functional_passed"]
                - api_main_summary["functional_passed"],
                "lite_delta_percentage_points": round(
                    100
                    * (
                        api_lite_summary["functional_pass_rate"]
                        - api_main_summary["functional_pass_rate"]
                    ),
                    3,
                ),
            },
            "local_vllm": {
                "main": local_main_summary,
                "lite_v1": local_lite_summary,
                "lite_delta_passes": local_lite_summary["functional_passed"]
                - local_main_summary["functional_passed"],
                "lite_delta_percentage_points": round(
                    100
                    * (
                        local_lite_summary["functional_pass_rate"]
                        - local_main_summary["functional_pass_rate"]
                    ),
                    3,
                ),
            },
        },
        "splits": {
            "api": {
                "main150": {
                    "main": api_main150_summary["functional_passed"],
                    "lite_v1": _split_counts(api_lite_index, main_ids),
                },
                "external50": {
                    "main": _split_counts(_suite_index(api_external50, 50), external_ids),
                    "lite_v1": _split_counts(api_lite_index, external_ids),
                },
            },
            "local_vllm": {
                "main150": {
                    "main": _split_counts(local_main_index, main_ids),
                    "lite_v1": _split_counts(local_lite_index, main_ids),
                },
                "external50": {
                    "main": _split_counts(local_main_index, external_ids),
                    "lite_v1": _split_counts(local_lite_index, external_ids),
                },
            },
        },
        "paired_functional_outcomes": {
            "api_python150": _paired_matrix(api_main150, api_lite, main_ids),
            "api_python200": _paired_matrix(api_main, api_lite, python200_ids),
            "local_vllm_python150": _paired_matrix(local_main, local_lite, main_ids),
            "local_vllm_python200": _paired_matrix(
                local_main, local_lite, python200_ids
            ),
        },
        "paired_rres": {
            "api_python150": _paired_rres(
                api_main150, api_lite, api_main150_results, api_lite_results, main_ids
            ),
            "api_python200": _paired_rres(
                api_main, api_lite, api_main_results, api_lite_results, python200_ids
            ),
            "local_vllm_python150": _paired_rres(
                local_main, local_lite, local_main_results, local_lite_results, main_ids
            ),
            "local_vllm_python200": _paired_rres(
                local_main,
                local_lite,
                local_main_results,
                local_lite_results,
                python200_ids,
            ),
        },
        "resource_diagnostics_not_core_metrics": {
            "api_python150": {
                "main": _usage(api_main150),
                "lite_v1": _usage(api_lite, main_ids),
            },
            "api_python200": {
                "main": _usage(api_main),
                "lite_v1": _usage(api_lite),
            },
            "local_vllm_python200": {
                "main": _usage(local_main),
                "lite_v1": _usage(local_lite),
            },
        },
        "data_quality": {
            "status": "complete_for_deepseek_main_vs_lite_v1_main_budget",
            "safe_to_cite": [
                "Functional Pass counts and rates for all four Python-200 conditions",
                "Complete primary failure-stage distributions for all four conditions",
                "Pass-conditioned RRES for all four conditions",
                "Paired RRES on both-pass subsets for API and local vLLM",
            ],
            "not_safe_to_claim": [
                "Lite V1 is more compact than Main",
                "Lite V1 improves Functional Pass",
                "Cross-model token counts are comparable costs",
                "Rescue+ Core-12 results belong in the Python-150/200 main table",
            ],
            "missing_evidence": [],
            "known_stale_label": (
                "Older results-pack READMEs labeled summary.passed as Functional "
                "pass; those values are run-status counts only. Older docs called "
                "the 120-step Lite V1 comparison Frozen Lite V1; that name is the "
                "45+10 envelope, not this comparison."
            ),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-main150-dir", type=Path, default=DEFAULT_API_MAIN150_DIR)
    parser.add_argument(
        "--api-external50-dir", type=Path, default=DEFAULT_API_EXTERNAL50_DIR
    )
    parser.add_argument("--api-lite-dir", type=Path, default=DEFAULT_API_LITE_DIR)
    parser.add_argument("--local-main-dir", type=Path, default=DEFAULT_LOCAL_MAIN_DIR)
    parser.add_argument("--local-lite-dir", type=Path, default=DEFAULT_LOCAL_LITE_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        args.api_main150_dir.resolve(),
        args.api_external50_dir.resolve(),
        args.api_lite_dir.resolve(),
        args.local_main_dir.resolve(),
        args.local_lite_dir.resolve(),
    )
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
