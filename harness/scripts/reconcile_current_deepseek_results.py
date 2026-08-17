#!/usr/bin/env python3
"""Reconcile current DeepSeek Main and Frozen Lite V1 result artifacts.

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
import hashlib
import json
import math
import statistics
import tarfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RESULTS_PACK = (
    REPO_ROOT
    / "experiments/python200-deepseek-v4-flash-lite-v1-vllm-local-0813-001-results-latest.tar.gz"
)
DEFAULT_API_MAIN150_PACK = (
    REPO_ROOT / "experiments/FeatureLiftBench-deepseek-v4-flash-150-20260805.tar.gz"
)
DEFAULT_OUTPUT = (
    REPO_ROOT
    / "artifacts/research_analysis/current_results/deepseek_main_vs_frozen_lite_v1_20260817.json"
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json_member(archive: tarfile.TarFile, member: str) -> dict[str, Any]:
    handle = archive.extractfile(member)
    if handle is None:
        raise FileNotFoundError(f"missing archive member: {member}")
    value = json.load(handle)
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {member}")
    return value


def _find_member(archive: tarfile.TarFile, suffix: str) -> str:
    matches = [name for name in archive.getnames() if name.endswith(suffix)]
    if len(matches) != 1:
        raise ValueError(f"expected one member ending with {suffix!r}, found {matches}")
    return matches[0]


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


def _load_detailed_results(
    archive: tarfile.TarFile,
    suite_member: str,
) -> dict[str, dict[str, Any]]:
    prefix = suite_member.rsplit("/", 1)[0] + "/"
    results: dict[str, dict[str, Any]] = {}
    for member in archive.getnames():
        if not member.startswith(prefix) or not member.endswith("/eval/result.json"):
            continue
        result = _load_json_member(archive, member)
        task_id = result.get("task_id")
        if not isinstance(task_id, str):
            raise TypeError(f"eval result missing task_id: {member}")
        results[task_id] = result
    return results


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


def _summarize_compact_only(
    suite: dict[str, Any], expected: int
) -> dict[str, Any]:
    index = _suite_index(suite, expected)
    functional_passed = sum(_functional_pass(run) for run in index.values())
    missing = sum(
        not _functional_pass(run) and run.get("status") == "missing_submission"
        for run in index.values()
    )
    stage_unavailable = expected - functional_passed - missing
    outcomes = {
        "functional_pass": functional_passed,
        "missing_submission": missing,
        "stage_evidence_unavailable": stage_unavailable,
    }
    return {
        "assigned": expected,
        "functional_passed": functional_passed,
        "functional_pass_rate": round(functional_passed / expected, 6),
        "run_status_passed": sum(run.get("status") == "passed" for run in index.values()),
        "eval_result_coverage": 0,
        "primary_outcomes": outcomes,
        "task_ids_by_primary_outcome": {
            "missing_submission": sorted(
                task_id
                for task_id, run in index.items()
                if not _functional_pass(run) and run.get("status") == "missing_submission"
            )
        },
        "rres": _rres_summary([], functional_passed),
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


def build_report(results_pack: Path, api_main150_pack: Path) -> dict[str, Any]:
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

    with tarfile.open(results_pack, "r:gz") as archive:
        api_aggregate = _load_json_member(archive, "./baselines/suite-aggregate.json")
        local_main = _load_json_member(
            archive, "./baselines/main-vllm-local-0812-001-suite.json"
        )
        api_lite = _load_json_member(
            archive, "./baselines/lite-v1-api-0812-002-suite.json"
        )
        local_lite_member = (
            "./python200-deepseek-v4-flash-lite-v1-vllm-local-0813-001/suite.json"
        )
        local_lite = _load_json_member(archive, local_lite_member)
        local_lite_results = _load_detailed_results(archive, local_lite_member)

    with tarfile.open(api_main150_pack, "r:gz") as archive:
        api_main150_member = _find_member(
            archive, "/deepseek-v4-flash-0731/suite.json"
        )
        api_main150 = _load_json_member(archive, api_main150_member)
        api_main150_results = _load_detailed_results(archive, api_main150_member)

    api_main150_summary = _summarize_detailed_suite(
        api_main150, api_main150_results, 150
    )
    api_lite_summary = _summarize_compact_only(api_lite, 200)
    local_main_summary = _summarize_compact_only(local_main, 200)
    local_lite_summary = _summarize_detailed_suite(
        local_lite, local_lite_results, 200
    )

    external_summary = next(
        item
        for item in api_aggregate.get("suites") or []
        if item.get("total") == 50
    )
    external_functional = float(external_summary["average_final_score"]) * int(
        external_summary["total"]
    )
    if not external_functional.is_integer():
        raise ValueError("External-50 binary final-score aggregate is non-integral")
    external_functional_passed = int(external_functional)

    api_main_summary = {
        "assigned": 200,
        "functional_passed": api_main150_summary["functional_passed"]
        + external_functional_passed,
        "functional_pass_rate": round(
            (api_main150_summary["functional_passed"] + external_functional_passed)
            / 200,
            6,
        ),
        "run_status_passed": int(api_aggregate["suites"][0]["passed"])
        + int(external_summary["passed"]),
        "eval_result_coverage": api_main150_summary["eval_result_coverage"],
        "primary_outcomes": dict(api_main150_summary["primary_outcomes"]),
        "rres": dict(api_main150_summary["rres"]),
        "external50_functional_passed": external_functional_passed,
        "external50_stage_evidence_unavailable": 50 - external_functional_passed,
    }
    api_main_summary["primary_outcomes"]["functional_pass"] = (
        api_main_summary["functional_passed"]
    )
    api_main_summary["primary_outcomes"]["stage_evidence_unavailable"] = (
        50 - external_functional_passed
    )
    api_main_summary["rres"]["eligible_functional_passes"] = (
        api_main_summary["functional_passed"]
    )
    api_main_summary["rres"]["coverage"] = round(
        api_main_summary["rres"]["available"]
        / api_main_summary["functional_passed"],
        6,
    )

    api_lite_index = _suite_index(api_lite, 200)
    local_main_index = _suite_index(local_main, 200)
    local_lite_index = _suite_index(local_lite, 200)
    api_main150_index = _suite_index(api_main150, 150)

    api_lite_main_passed = sum(
        _functional_pass(api_lite_index[task_id]) for task_id in main_ids
    )
    api_lite_external_passed = sum(
        _functional_pass(api_lite_index[task_id]) for task_id in external_ids
    )
    local_main_main_passed = sum(
        _functional_pass(local_main_index[task_id]) for task_id in main_ids
    )
    local_main_external_passed = sum(
        _functional_pass(local_main_index[task_id]) for task_id in external_ids
    )
    local_lite_main_passed = sum(
        _functional_pass(local_lite_index[task_id]) for task_id in main_ids
    )
    local_lite_external_passed = sum(
        _functional_pass(local_lite_index[task_id]) for task_id in external_ids
    )

    return {
        "schema_version": "featureliftbench.current_result_reconciliation.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
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
            "results_pack": {
                "path": str(results_pack.relative_to(REPO_ROOT)),
                "sha256": _sha256(results_pack),
            },
            "api_main150_pack": {
                "path": str(api_main150_pack.relative_to(REPO_ROOT)),
                "sha256": _sha256(api_main150_pack),
            },
        },
        "headline": {
            "api": {
                "main": api_main_summary,
                "frozen_lite_v1": api_lite_summary,
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
                "frozen_lite_v1": local_lite_summary,
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
                    "frozen_lite_v1": api_lite_main_passed,
                },
                "external50": {
                    "main": external_functional_passed,
                    "frozen_lite_v1": api_lite_external_passed,
                },
            },
            "local_vllm": {
                "main150": {
                    "main": local_main_main_passed,
                    "frozen_lite_v1": local_lite_main_passed,
                },
                "external50": {
                    "main": local_main_external_passed,
                    "frozen_lite_v1": local_lite_external_passed,
                },
            },
        },
        "paired_functional_outcomes": {
            "api_main150": _paired_matrix(api_main150, api_lite, main_ids),
            "local_vllm_python200": _paired_matrix(
                local_main, local_lite, main_ids | external_ids
            ),
        },
        "resource_diagnostics_not_core_metrics": {
            "api_main150": {
                "main": _usage(api_main150),
                "frozen_lite_v1": _usage(api_lite, main_ids),
            },
            "local_vllm_python200": {
                "main": _usage(local_main),
                "frozen_lite_v1": _usage(local_lite),
            },
        },
        "data_quality": {
            "status": "partial_for_rres_and_failure_stage_comparison",
            "safe_to_cite": [
                "Functional Pass counts and rates for all four Python-200 conditions",
                "API Main-150 and local Lite V1 primary failure-stage distributions",
                "API Main-150 and local Lite V1 pass-conditioned RRES summaries",
            ],
            "not_safe_to_claim": [
                "A paired Main-versus-Lite RRES difference",
                "A complete API Main-200 per-task failure-stage distribution",
                "API Lite V1 or local Main failure-stage distributions",
            ],
            "missing_evidence": [
                "API Main External-50 per-task eval/result.json",
                "API Lite V1 per-task eval/result.json",
                "local vLLM Main per-task eval/result.json",
            ],
            "known_stale_label": (
                "The results-pack README labels historical summary.passed counts "
                "as Functional pass; those values are run-status counts only."
            ),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-pack", type=Path, default=DEFAULT_RESULTS_PACK)
    parser.add_argument("--api-main150-pack", type=Path, default=DEFAULT_API_MAIN150_PACK)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(args.results_pack.resolve(), args.api_main150_pack.resolve())
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
