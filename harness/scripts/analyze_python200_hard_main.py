#!/usr/bin/env python3
"""Build a paper-facing audit of one Python-200' (150 + Hard-50) suite."""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SELECTION = ROOT / "benchmark/selection/python200_hard_suite.json"
DEFAULT_REGISTRY = ROOT / "benchmark/sources/python200_hard_registry.json"
DEFAULT_TAXONOMY = ROOT / "artifacts/research_analysis/python200_hard_task_taxonomy.csv"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> list[float]:
    if total == 0:
        return [0.0, 0.0]
    rate = successes / total
    denominator = 1 + z * z / total
    center = (rate + z * z / (2 * total)) / denominator
    margin = z * math.sqrt(rate * (1 - rate) / total + z * z / (4 * total * total)) / denominator
    return [center - margin, center + margin]


def median(values: Iterable[float | int | None]) -> float | None:
    clean = [float(value) for value in values if value is not None]
    return statistics.median(clean) if clean else None


def rate_record(rows: list[dict[str, Any]]) -> dict[str, Any]:
    passed = sum(bool(row["functional_pass"]) for row in rows)
    total = len(rows)
    return {
        "passed": passed,
        "total": total,
        "rate": passed / total if total else None,
        "wilson_95": wilson_interval(passed, total),
    }


def first_failure_stage(result: dict[str, Any] | None) -> str:
    if result is None:
        return "missing_submission"
    if float((result.get("scores") or {}).get("final_score") or 0.0) >= 1.0:
        return "pass"
    if not result.get("build_pass"):
        return "build"
    if not result.get("public_tests_pass"):
        return "public"
    if not result.get("hidden_tests_pass"):
        return "hidden"
    if not result.get("isolation_pass"):
        return "isolation"
    return "other"


def load_taxonomy(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["task_id"]: row for row in csv.DictReader(handle)}


def registry_snapshots(path: Path) -> dict[str, set[str]]:
    payload = read_json(path)
    by_task: dict[str, set[str]] = {}
    for repository in payload.get("repositories", []):
        snapshots = {str(value) for value in repository.get("snapshot_ids", [])}
        for task_id in repository.get("task_ids", []):
            by_task[str(task_id)] = snapshots
    return by_task


def task_row(
    suite_dir: Path,
    run: dict[str, Any],
    taxonomy: dict[str, dict[str, str]],
    registry: dict[str, set[str]],
) -> dict[str, Any]:
    task_id = str(run["task_id"])
    task_dir = suite_dir / task_id
    run_path = task_dir / "run.json"
    result_path = task_dir / "eval/result.json"
    usage_path = task_dir / "agent/openhands_usage.json"
    task_run = read_json(run_path) if run_path.is_file() else run
    result = read_json(result_path) if result_path.is_file() else None
    usage = read_json(usage_path) if usage_path.is_file() else {}
    tax = taxonomy.get(task_id, {})
    scores = (result or {}).get("scores") or {}
    compactness = (result or {}).get("compactness") or {}
    context_audit = usage.get("context_audit") or {}
    source = task_run.get("source") or run.get("source") or {}
    agent = task_run.get("agent") or {}
    run_errors = [str(value) for value in task_run.get("errors") or []]
    freeze_preflight_blocked = any(
        "active benchmark freeze spec hash mismatch" in value for value in run_errors
    )
    dependency_install = (result or {}).get("dependency_install") or {}
    dependency_install_failed = bool(result) and not dependency_install.get("passed", False)
    source_snapshot_id = source.get("source_snapshot_id")
    allowed_snapshots = registry.get(task_id, set())
    source_snapshot_match = (
        source_snapshot_id in allowed_snapshots if source_snapshot_id else None
    )
    final_score = float(scores.get("final_score") or 0.0)
    if freeze_preflight_blocked:
        audit_failure_class = "freeze_preflight_blocked"
    elif result is None:
        audit_failure_class = "agent_no_submission"
    elif dependency_install_failed:
        audit_failure_class = "dependency_install_infrastructure"
    elif final_score >= 1.0:
        audit_failure_class = "pass"
    elif not result.get("build_pass"):
        audit_failure_class = "submission_build"
    elif not result.get("public_tests_pass"):
        audit_failure_class = "public_behavior"
    elif not result.get("hidden_tests_pass"):
        audit_failure_class = "hidden_only_behavior"
    elif not result.get("isolation_pass"):
        audit_failure_class = "isolation"
    else:
        audit_failure_class = "other"
    max_prompt = context_audit.get("max_prompt_tokens_per_call")
    max_allowed = context_audit.get("max_allowed_prompt_tokens")
    return {
        "task_id": task_id,
        "suite_split": tax.get("suite_split") or "unknown",
        "lift_type": tax.get("lift_type") or "unknown",
        "feature_family": tax.get("feature_family_v2") or "unknown",
        "copytrap": tax.get("copytrap") or "unknown",
        "functional_pass": final_score >= 1.0,
        "failure_stage": first_failure_stage(result),
        "audit_failure_class": audit_failure_class,
        "run_status": task_run.get("status") or run.get("status") or "unknown",
        "failure_class": task_run.get("failure_class") or run.get("failure_class") or "unknown",
        "final_score": final_score,
        "reference_relative_loc_ratio": scores.get("reference_relative_loc_ratio"),
        "compactness_class": compactness.get("compactness_class"),
        "copied_fraction": compactness.get("copied_fraction"),
        "submitted_loc": compactness.get("submitted_loc"),
        "total_tokens": usage.get("total_tokens"),
        "effective_uncached_prompt_tokens": usage.get("effective_uncached_prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "api_calls": usage.get("api_calls"),
        "context_violation": context_audit.get("context_violation"),
        "max_prompt_tokens_per_call": max_prompt,
        "max_allowed_prompt_tokens": max_allowed,
        "context_overage_tokens": (
            int(max_prompt) - int(max_allowed)
            if max_prompt is not None and max_allowed is not None
            else None
        ),
        "agent_attempted": bool(agent.get("command")),
        "freeze_preflight_blocked": freeze_preflight_blocked,
        "dependency_install_failed": dependency_install_failed,
        "dependency_failure_reason": dependency_install.get("reason") or "",
        "run_error": run_errors[0] if run_errors else "",
        "source_snapshot_id": source_snapshot_id,
        "source_snapshot_match": source_snapshot_match,
    }


def grouped_rates(rows: list[dict[str, Any]], field: str) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row.get(field) or "unknown")].append(row)
    return {key: rate_record(value) for key, value in sorted(groups.items())}


def grouped_stage_counts(rows: list[dict[str, Any]], field: str) -> dict[str, dict[str, int]]:
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        groups[str(row.get(field) or "unknown")][str(row["failure_stage"])] += 1
    return {key: dict(sorted(value.items())) for key, value in sorted(groups.items())}


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def pct(value: float | None) -> str:
    return "—" if value is None else f"{value:.1%}"


def make_markdown(summary: dict[str, Any]) -> str:
    headline = summary["headline"]
    split = summary["by_split"]
    context = summary["context_audit"]
    lines = [
        "# Python-200′ DeepSeek V4 Flash Main — 2026-08-29",
        "",
        "> **Status: current candidate evidence · Last verified: 2026-08-29**",
        "",
        "## Technical summary",
        "",
        f"The received suite records **{headline['passed']}/{headline['total']} "
        f"({pct(headline['rate'])})** functional passes on the Python-200′ selection, but "
        "it is not a complete eligible 200-task Main run. Seventeen Python-150 tasks were "
        "blocked before agent launch by freeze-spec mismatches, 16 Hard-50 evaluations "
        "failed because required offline dependencies were unavailable, and "
        f"{context['violation_runs']} runs exceeded the prompt allowance. The union is "
        f"{summary['eligibility']['strict_rerun_union']} tasks, so 132/200 is an "
        "**audit headline**, not a paper leaderboard result.",
        "",
        "## The split rates are descriptive but infrastructure-confounded",
        "",
        "| Split | Functional Pass | Rate | Wilson 95% interval |",
        "| --- | ---: | ---: | ---: |",
    ]
    for key in ("python150", "hard50"):
        item = split[key]
        label = "Frozen Python-150" if key == "python150" else "Hard-50"
        ci = item["wilson_95"]
        lines.append(
            f"| {label} | {item['passed']}/{item['total']} | {pct(item['rate'])} | "
            f"{pct(ci[0])}–{pct(ci[1])} |"
        )
    lines.extend(
        [
            f"| **Python-200′** | **{headline['passed']}/{headline['total']}** | "
            f"**{pct(headline['rate'])}** | **{pct(headline['wilson_95'][0])}–"
            f"{pct(headline['wilson_95'][1])}** |",
            "",
            "These raw split rates cannot be interpreted as a clean difficulty contrast: "
            "all 17 freeze-preflight blocks are in Python-150, while all 16 dependency "
            "installation failures are in Hard-50. The earlier independent Hard-50 "
            "calibration remains useful design evidence, but this received suite must be "
            "repaired before it supports a new main-table split comparison. Historical "
            "E50 runs also differ in date, runtime image, and endpoint.",
            "",
            "## Infrastructure and model failures must be separated",
            "",
            "| First functional outcome | Tasks | Share of 200 |",
            "| --- | ---: | ---: |",
        ]
    )
    for stage in ("pass", "missing_submission", "build", "public", "hidden", "isolation", "other"):
        count = summary["failure_stages"].get(stage, 0)
        if count:
            lines.append(f"| {stage} | {count} | {count / headline['total']:.1%} |")
    lines.extend(
        [
            "",
            f"Of the 68 nominal non-passes, {summary['audit_failure_classes'].get('freeze_preflight_blocked', 0)} "
            "are pre-agent freeze blocks and "
            f"{summary['audit_failure_classes'].get('dependency_install_infrastructure', 0)} "
            "are offline dependency failures. The model/output evidence is therefore "
            f"{summary['audit_failure_classes'].get('agent_no_submission', 0)} no-submission, "
            f"{summary['audit_failure_classes'].get('public_behavior', 0)} public-behavior, and "
            f"{summary['audit_failure_classes'].get('hidden_only_behavior', 0)} hidden-only "
            "failures. There are no isolation failures.",
            "",
            "## Workflow status is not the paper metric",
            "",
            f"Only **{summary['workflow_status'].get('passed', 0)}/200** runs have workflow "
            f"status `passed`, while **{headline['passed']}/200** pass the functional "
            "evaluator. The paper and leaderboard must use `final_score` / Functional "
            "Pass@1, not the agent-process status field.",
            "",
            "## Provenance and robustness gate",
            "",
            f"- Task-set identity: {summary['identity']['task_set_matches']}/200 task IDs match; "
            f"{summary['identity']['extra_task_count']} extra and "
            f"{summary['identity']['missing_task_count']} missing.",
            f"- Source identity: {summary['identity']['source_snapshot_matches']} started tasks "
            "match the source registry; missing source IDs occur only where no run provenance "
            "was emitted.",
            f"- Runtime identity: agent and evaluator Docker image digests are recorded; "
            f"network-isolated evaluator failures = {summary['runtime']['docker_sandbox_failures']}.",
            f"- Preflight: {summary['eligibility']['freeze_preflight_blocked']} tasks never "
            "launched because their active spec hash disagreed with the freeze.",
            f"- Dependency environment: {summary['eligibility']['dependency_install_failures']} "
            "tasks failed before behavioral tests because required offline wheels were absent.",
            f"- Context audit: {context['violation_runs']} runs exceeded the configured "
            f"prompt allowance at least once; {context['violation_passes']} of them passed. "
            "This is the main eligibility blocker.",
            "- The suite records no benchmark freeze identifier. The task set can be "
            "reconstructed from IDs and registry snapshots, but final paper provenance should "
            "explicitly bind the recorded run to the active freeze.",
            "",
            "## What this adds to the paper",
            "",
            "1. **RQ1 has an audit-ready candidate, not a completed cell.** The suite exposes "
            "exactly which tasks require clean replacement runs.",
            "2. **Failure attribution improves materially.** Infrastructure blocks are no "
            "longer misreported as model failures.",
            "3. **The taxonomy and compactness layers are ready.** They can be reused once the "
            "strict replacement set is complete.",
            "4. **The result cannot enter the final leaderboard.** The current headline is "
            "useful for internal planning only.",
            "",
            "## Recommended next steps",
            "",
            f"1. Use the frozen {summary['eligibility']['strict_rerun_union']}-task union: "
            "59 context violations, 17 freeze-preflight blocks, and 16 dependency failures "
            "with overlap removed.",
            "2. Repair/pin the offline wheel set before rerunning dependency failures.",
            "3. Bind every replacement run to the active benchmark freeze and preserve the "
            "original candidate unchanged.",
            "4. Keep the two genuine no-submission outcomes and 33 behavioral failures as "
            "observed evidence unless a preregistered full-repeat policy says otherwise.",
            "",
            "## Further questions",
            "",
            "- What is the eligible Functional Pass@1 after the fixed 84-task replacement set?",
            "- How many context-violation outcomes change under strict enforcement?",
            "- Are Hard-50 failures concentrated by lift type or feature family after "
            "multiple-comparison-aware uncertainty reporting?",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("suite_dir", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--taxonomy", type=Path, default=DEFAULT_TAXONOMY)
    args = parser.parse_args()

    suite_dir = args.suite_dir.resolve()
    suite = read_json(suite_dir / "suite.json")
    selection = read_json(args.selection)
    taxonomy = load_taxonomy(args.taxonomy)
    registry = registry_snapshots(args.registry)
    rows = [task_row(suite_dir, run, taxonomy, registry) for run in suite["runs"]]
    expected = {str(value) for value in selection["task_ids"]}
    actual = {row["task_id"] for row in rows}
    usage = suite.get("agent_usage_totals") or {}
    context_groups = {
        "violation": [row for row in rows if row["context_violation"] is True],
        "compliant": [row for row in rows if row["context_violation"] is False],
        "unavailable": [row for row in rows if row["context_violation"] is None],
    }
    freeze_blocked = [row for row in rows if row["freeze_preflight_blocked"]]
    dependency_failures = [row for row in rows if row["dependency_install_failed"]]
    strict_rerun_ids = sorted(
        {
            row["task_id"]
            for row in rows
            if row["context_violation"] is True
            or row["freeze_preflight_blocked"]
            or row["dependency_install_failed"]
        }
    )
    fixed_eligible_rows = [row for row in rows if row["task_id"] not in strict_rerun_ids]
    summary = {
        "schema_version": "featureliftbench.python200_hard_main_analysis.v1",
        "suite": suite_dir.name,
        "generated_at": suite.get("generated_at"),
        "model": (suite.get("agent_config") or {}).get("model"),
        "profile": (suite.get("agent_config") or {}).get("profile"),
        "headline": rate_record(rows),
        "by_split": grouped_rates(rows, "suite_split"),
        "by_lift_type": grouped_rates(rows, "lift_type"),
        "by_copytrap": grouped_rates(rows, "copytrap"),
        "failure_stages": dict(sorted(Counter(row["failure_stage"] for row in rows).items())),
        "audit_failure_classes": dict(
            sorted(Counter(str(row["audit_failure_class"]) for row in rows).items())
        ),
        "failure_stages_by_split": grouped_stage_counts(rows, "suite_split"),
        "workflow_status": dict(sorted(Counter(str(row["run_status"]) for row in rows).items())),
        "workflow_functional_crosstab": {
            f"{row['run_status']}|{'pass' if row['functional_pass'] else 'fail'}": sum(
                other["run_status"] == row["run_status"]
                and other["functional_pass"] == row["functional_pass"]
                for other in rows
            )
            for row in rows
        },
        "compactness": {
            "class_counts_on_passes": dict(
                sorted(
                    Counter(
                        str(row["compactness_class"] or "unknown")
                        for row in rows
                        if row["functional_pass"]
                    ).items()
                )
            ),
            "pass_rres_median": median(
                row["reference_relative_loc_ratio"]
                for row in rows
                if row["functional_pass"]
            ),
            "pass_rres_median_by_split": {
                split: median(
                    row["reference_relative_loc_ratio"]
                    for row in rows
                    if row["functional_pass"] and row["suite_split"] == split
                )
                for split in sorted({str(row["suite_split"]) for row in rows})
            },
        },
        "usage": {
            "available_runs": usage.get("available_runs"),
            "missing_runs": usage.get("missing_runs"),
            "total_tokens": usage.get("total_tokens"),
            "effective_uncached_prompt_tokens": usage.get("effective_uncached_prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "prompt_cache_hit_rate": usage.get("prompt_cache_hit_rate"),
            "context_violation_runs": (usage.get("context_audit") or {}).get("context_violation_runs"),
            "median_total_tokens_pass": median(
                row["total_tokens"] for row in rows if row["functional_pass"]
            ),
            "median_total_tokens_fail": median(
                row["total_tokens"] for row in rows if not row["functional_pass"]
            ),
        },
        "context_audit": {
            "violation_runs": len(context_groups["violation"]),
            "violation_passes": sum(
                row["functional_pass"] for row in context_groups["violation"]
            ),
            "violation_rate": rate_record(context_groups["violation"]),
            "compliant_rate": rate_record(context_groups["compliant"]),
            "unavailable_rate": rate_record(context_groups["unavailable"]),
            "strict_lower_bound_if_violations_invalidated": sum(
                row["functional_pass"] for row in context_groups["compliant"]
            ) / len(rows),
        },
        "eligibility": {
            "agent_attempted": sum(row["agent_attempted"] for row in rows),
            "freeze_preflight_blocked": len(freeze_blocked),
            "dependency_install_failures": len(dependency_failures),
            "context_violation_runs": len(context_groups["violation"]),
            "strict_rerun_union": len(strict_rerun_ids),
            "strict_rerun_task_ids": strict_rerun_ids,
            "fixed_eligible_tasks": len(fixed_eligible_rows),
            "fixed_eligible_passes": sum(row["functional_pass"] for row in fixed_eligible_rows),
            "final_pass_count_range_before_rerun": [
                sum(row["functional_pass"] for row in fixed_eligible_rows),
                sum(row["functional_pass"] for row in fixed_eligible_rows) + len(strict_rerun_ids),
            ],
        },
        "identity": {
            "expected_suite_id": selection.get("suite_id"),
            "task_set_sha256": selection.get("task_set_sha256"),
            "baseline_freeze_id": selection.get("baseline_freeze_id"),
            "hard50_selection_id": selection.get("hard50_selection_id"),
            "task_set_matches": len(expected & actual),
            "missing_task_count": len(expected - actual),
            "extra_task_count": len(actual - expected),
            "source_snapshot_matches": sum(row["source_snapshot_match"] is True for row in rows),
            "source_snapshot_mismatches": sum(row["source_snapshot_match"] is False for row in rows),
            "source_snapshot_unavailable": sum(row["source_snapshot_match"] is None for row in rows),
            "recorded_benchmark_freeze_id": (
                (suite.get("runs") or [{}])[0].get("experiment_conditions") or {}
            ).get("benchmark_freeze_id"),
        },
        "runtime": {
            "agent_backend": suite.get("agent_backend"),
            "agent_docker_image": suite.get("agent_docker_image"),
            "eval_backend": suite.get("eval_backend"),
            "eval_docker_image": suite.get("eval_docker_image"),
            "docker_sandbox_failures": (suite.get("summary") or {}).get("docker_sandbox_failures"),
        },
    }
    summary["workflow_functional_crosstab"] = dict(
        sorted(Counter(f"{row['run_status']}|{'pass' if row['functional_pass'] else 'fail'}" for row in rows).items())
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    write_csv(args.output_dir / "task_results.csv", rows)
    (args.output_dir / "paper_readout.md").write_text(make_markdown(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
