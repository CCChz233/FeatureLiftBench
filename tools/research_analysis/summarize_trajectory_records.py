#!/usr/bin/env python3
"""Validate and summarize trajectory_records.csv without re-reading trajectories."""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Iterable


REQUIRED_SCHEMA = (
    "task_id",
    "run_id",
    "model",
    "agent",
    "public_pass",
    "hidden_pass",
    "functional_pass",
    "extraction_ratio",
    "final_score",
    "copied_file_count",
    "copied_loc",
    "repeated_file_reads",
    "repeated_line_reads",
    "tool_error_count",
    "harness_format_error_count",
    "closure_plan_present",
    "self_generated_tests",
    "hidden_risk_discussed",
    "stop_reason",
    "primary_failure",
    "secondary_failure",
    "trajectory_path",
    "evaluation_path",
    "evidence_step_ids",
)


STRUCTURAL_FIELDS = (
    "task_id",
    "run_id",
    "model",
    "agent",
    "functional_pass",
    "stop_reason",
    "primary_failure",
    "trajectory_path",
    "evaluation_path",
    "evidence_step_ids",
)


CASE_SELECTORS = (
    ("deepseek/deepseek-v4-flash", "requests_cache__cache_key_core__hard3_001"),
    ("deepseek/deepseek-v4-flash", "pydantic_v1__validation_error_core__001"),
    ("deepseek/deepseek-v4-flash", "phonenumbers__parse_format_core__001"),
    ("deepseek/deepseek-v4-flash", "diskcache__eviction_policy_core__hard3_001"),
    ("deepseek/deepseek-v4-flash", "click__lazy_command_core__hard3_001"),
    ("deepseek/deepseek-v4-flash", "pytest__marker_registry_core__hard3_001"),
    ("deepseek/deepseek-v4-flash", "jupyter_server__extension_config_core__hard3_001"),
    ("deepseek/deepseek-v4-flash", "parsel__selector_namespace_core__hard3_001"),
    ("deepseek/deepseek-v4-flash", "sqlalchemy__event_dispatch_core__hard3_001"),
    ("deepseek/deepseek-v4-flash", "stevedore__extension_manager_core__hard3_001"),
    ("deepseek/deepseek-v4-flash", "pluggy__hook_wrapper_core__hard3_001"),
    ("deepseek/deepseek-v4-flash", "pydantic__field_validator_core__hard3_001"),
    ("deepseek/deepseek-v4-flash", "coverage__config_merge_core__001"),
    ("deepseek/deepseek-v4-flash", "dynaconf__settings_merge_core__001"),
    ("deepseek/deepseek-v4-flash", "sphinx__extension_registry_core__hard3_001"),
    ("deepseek/deepseek-v4-flash", "readme_renderer__content_type_core__hard3_001"),
    ("deepseek/deepseek-v4-flash", "bleach__sanitize_core__001"),
    ("deepseek/deepseek-v4-flash", "responses__request_matcher_core__hard3_001"),
    ("deepseek/deepseek-v4-flash", "yamale__schema_validate_core__hard3_001"),
    ("openai/Qwen3-Coder-30B-A3B-Instruct", "pyyaml__safe_load_dump__001"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parents[2]
    parser.add_argument(
        "--input",
        type=Path,
        default=root / "artifacts/research_analysis/trajectory_records.csv",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=root / "artifacts/research_analysis/trajectory_statistics.json",
    )
    parser.add_argument(
        "--output-markdown",
        type=Path,
        default=root / "artifacts/research_analysis/trajectory_statistics.md",
    )
    parser.add_argument(
        "--output-extremes",
        type=Path,
        default=root / "artifacts/research_analysis/extraction_extremes.csv",
    )
    parser.add_argument("--check-paths", action="store_true")
    return parser.parse_args()


def bool_value(value: str) -> bool | None:
    lowered = value.strip().lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    return None


def int_value(value: str) -> int | None:
    if not value.strip():
        return None
    return int(float(value))


def float_value(value: str) -> float | None:
    if not value.strip():
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def rate(count: int, denominator: int) -> dict[str, Any]:
    return {
        "count": count,
        "denominator": denominator,
        "rate": round(count / denominator, 6) if denominator else None,
    }


def fmt_rate(item: dict[str, Any], digits: int = 1) -> str:
    value = item.get("rate")
    if value is None:
        return f"{item['count']}/{item['denominator']} (NA)"
    return f"{item['count']}/{item['denominator']} ({value * 100:.{digits}f}%)"


def median(values: Iterable[float | int | None]) -> float | None:
    clean = [float(value) for value in values if value is not None]
    return round(statistics.median(clean), 6) if clean else None


def mean(values: Iterable[float | int | None]) -> float | None:
    clean = [float(value) for value in values if value is not None]
    return round(statistics.fmean(clean), 6) if clean else None


def load_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])
    missing = sorted(set(REQUIRED_SCHEMA) - set(fieldnames))
    if missing:
        raise ValueError(f"input is missing required columns: {missing}")
    if not rows:
        raise ValueError("input CSV has no records")
    duplicate_ids = [key for key, count in Counter(r["run_id"] for r in rows).items() if count > 1]
    if duplicate_ids:
        raise ValueError(f"duplicate run_id values: {duplicate_ids[:5]}")
    return fieldnames, rows


def selected(rows: list[dict[str, str]], predicate: Callable[[dict[str, str]], bool]) -> list[dict[str, str]]:
    return [row for row in rows if predicate(row)]


def summarize_group(rows: list[dict[str, str]], *, label: str) -> dict[str, Any]:
    total = len(rows)
    public_observed = selected(rows, lambda r: bool_value(r["public_pass"]) is not None)
    hidden_observed = selected(rows, lambda r: bool_value(r["hidden_pass"]) is not None)
    public_pass = selected(rows, lambda r: bool_value(r["public_pass"]) is True)
    phhf = selected(
        rows,
        lambda r: bool_value(r["public_pass"]) is True and bool_value(r["hidden_pass"]) is False,
    )
    known_ratio = selected(rows, lambda r: float_value(r["extraction_ratio"]) is not None)
    return {
        "label": label,
        "runs": total,
        "strict_suite_pass": rate(sum(r["run_status"] == "passed" for r in rows), total),
        "functional_pass": rate(sum(bool_value(r["functional_pass"]) is True for r in rows), total),
        "public_observed": rate(len(public_observed), total),
        "public_pass_among_observed": rate(len(public_pass), len(public_observed)),
        "hidden_observed": rate(len(hidden_observed), total),
        "hidden_pass_among_observed": rate(
            sum(bool_value(r["hidden_pass"]) is True for r in hidden_observed), len(hidden_observed)
        ),
        "public_hidden_fail_total": rate(len(phhf), total),
        "public_hidden_fail_given_public_pass": rate(len(phhf), len(public_pass)),
        "environment_error": rate(
            sum((int_value(r["evaluator_environment_error_count"]) or 0) > 0 for r in rows), total
        ),
        "low_ratio": rate(
            sum((float_value(r["extraction_ratio"]) or math.inf) <= 0.25 for r in known_ratio),
            len(known_ratio),
        ),
        "high_ratio": rate(
            sum((float_value(r["extraction_ratio"]) or -math.inf) > 0.80 for r in known_ratio),
            len(known_ratio),
        ),
        "median_extraction_ratio": median(float_value(r["extraction_ratio"]) for r in rows),
        "median_final_score": median(float_value(r["final_score"]) for r in rows),
        "median_tokens": median(int_value(r["total_tokens"]) for r in rows),
        "median_tool_calls": median(int_value(r["tool_call_count"]) for r in rows),
        "median_copied_file_count": median(int_value(r["copied_file_count"]) for r in rows),
        "closure_plan_present": rate(sum(bool_value(r["closure_plan_present"]) is True for r in rows), total),
        "self_generated_tests": rate(sum(bool_value(r["self_generated_tests"]) is True for r in rows), total),
        "hidden_risk_discussed": rate(sum(bool_value(r["hidden_risk_discussed"]) is True for r in rows), total),
        "explicit_finish": rate(sum(r["stop_reason"] == "explicit_finish" for r in rows), total),
        "repeated_file_read_affected": rate(
            sum((int_value(r["repeated_file_reads"]) or 0) > 0 for r in rows), total
        ),
        "unsupported_completion_claim": rate(
            sum(bool_value(r["unsupported_completion_claim"]) is True for r in rows), total
        ),
    }


def grouped(rows: list[dict[str, str]], key: str) -> list[dict[str, Any]]:
    buckets: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        buckets[row.get(key) or "unknown"].append(row)
    result = [summarize_group(group_rows, label=label) for label, group_rows in buckets.items()]
    result.sort(key=lambda item: (-item["runs"], item["label"]))
    return result


def repeated_summary(rows: list[dict[str, str]]) -> dict[str, Any]:
    total = len(rows)
    result: dict[str, Any] = {}
    for field in (
        "repeated_file_reads",
        "repeated_line_reads",
        "repeated_terminal_commands",
        "tool_error_count",
        "harness_format_error_count",
        "agent_reasoning_error_count",
        "evaluator_environment_error_count",
    ):
        values = [int_value(row[field]) or 0 for row in rows]
        result[field] = {
            "affected_runs": rate(sum(value > 0 for value in values), total),
            "event_count": sum(values),
            "median_among_affected": median(value for value in values if value > 0),
        }
    return result


def extraction_summary(rows: list[dict[str, str]]) -> dict[str, Any]:
    known = [row for row in rows if float_value(row["extraction_ratio"]) is not None]
    buckets = {
        "under_proxy_le_0_25": [row for row in known if float_value(row["extraction_ratio"]) <= 0.25],
        "middle_0_25_to_0_80": [
            row for row in known if 0.25 < float_value(row["extraction_ratio"]) <= 0.80
        ],
        "over_proxy_gt_0_80": [row for row in known if float_value(row["extraction_ratio"]) > 0.80],
    }
    output: dict[str, Any] = {"known_ratio_runs": len(known), "unknown_ratio_runs": len(rows) - len(known)}
    for name, bucket in buckets.items():
        output[name] = summarize_group(bucket, label=name)
    return output


def error_source_summary(rows: list[dict[str, str]]) -> dict[str, Any]:
    total = len(rows)
    non_env_failures = [
        row
        for row in rows
        if bool_value(row["functional_pass"]) is False
        and (int_value(row["evaluator_environment_error_count"]) or 0) == 0
    ]
    return {
        "agent_reasoning_unsupported_completion_claim": {
            "definition": "FinishAction asserts completion/test success but final functional gate is 0, excluding evaluator/environment errors.",
            "all_runs": rate(sum(bool_value(r["unsupported_completion_claim"]) is True for r in rows), total),
            "non_environment_failures": rate(
                sum(bool_value(r["unsupported_completion_claim"]) is True for r in non_env_failures),
                len(non_env_failures),
            ),
        },
        "tool_execution_error": {
            "definition": "OpenHands ObservationEvent has is_error=true, excluding tool-schema validation errors.",
            "affected_runs": rate(sum((int_value(r["tool_error_count"]) or 0) > 0 for r in rows), total),
            "events": sum(int_value(r["tool_error_count"]) or 0 for r in rows),
        },
        "harness_format_error": {
            "definition": "Agent/Conversation error explicitly reports tool validation/schema/required-parameter failure.",
            "affected_runs": rate(
                sum((int_value(r["harness_format_error_count"]) or 0) > 0 for r in rows), total
            ),
            "events": sum(int_value(r["harness_format_error_count"]) or 0 for r in rows),
        },
        "evaluator_environment_error": {
            "definition": "Dependency installation, evaluator tooling, or Docker sandbox fails before a valid test outcome.",
            "affected_runs": rate(
                sum((int_value(r["evaluator_environment_error_count"]) or 0) > 0 for r in rows), total
            ),
            "events": sum(int_value(r["evaluator_environment_error_count"]) or 0 for r in rows),
        },
    }


def completeness(fieldnames: list[str], rows: list[dict[str, str]]) -> dict[str, Any]:
    total = len(rows)
    by_field = {
        field: {
            "nonempty": sum(bool(row.get(field, "").strip()) for row in rows),
            "denominator": total,
            "completeness": round(sum(bool(row.get(field, "").strip()) for row in rows) / total, 6),
        }
        for field in REQUIRED_SCHEMA
    }
    structural_cells = len(STRUCTURAL_FIELDS) * total
    structural_nonempty = sum(bool(row.get(field, "").strip()) for row in rows for field in STRUCTURAL_FIELDS)
    return {
        "rows": total,
        "columns": len(fieldnames),
        "required_schema_columns": len(REQUIRED_SCHEMA),
        "unique_run_ids": len({row["run_id"] for row in rows}),
        "structural_field_cell_completeness": rate(structural_nonempty, structural_cells),
        "by_required_field": by_field,
        "evaluation_available": rate(sum(bool_value(r["evaluation_available"]) is True for r in rows), total),
        "events_available": rate(sum(bool_value(r["events_available"]) is True for r in rows), total),
    }


def case_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    index = {(row["model"], row["task_id"]): row for row in rows}
    result: list[dict[str, Any]] = []
    for model, task_id in CASE_SELECTORS:
        row = index.get((model, task_id))
        if row is None:
            continue
        result.append(
            {
                "task_id": task_id,
                "model": model,
                "public_pass": row["public_pass"] or "NA",
                "hidden_pass": row["hidden_pass"] or "NA",
                "functional_pass": row["functional_pass"],
                "extraction_ratio": float_value(row["extraction_ratio"]),
                "final_score": float_value(row["final_score"]),
                "copied_file_count": int_value(row["copied_file_count"]),
                "copied_loc": int_value(row["copied_loc"]),
                "repeated_file_reads": int_value(row["repeated_file_reads"]) or 0,
                "tool_errors": int_value(row["tool_error_count"]) or 0,
                "harness_errors": int_value(row["harness_format_error_count"]) or 0,
                "tokens": int_value(row["total_tokens"]),
                "stop_reason": row["stop_reason"],
                "primary_failure": row["primary_failure"],
                "contract_review_required": bool_value(row["contract_review_required"]),
                "trajectory_path": row["trajectory_path"],
                "evaluation_path": row["evaluation_path"],
                "evidence_step_ids": json.loads(row["evidence_step_ids"] or "[]"),
            }
        )
    return result


def build_payload(fieldnames: list[str], rows: list[dict[str, str]], input_path: Path) -> dict[str, Any]:
    total = len(rows)
    primary_counts = Counter(row["primary_failure"] for row in rows)
    stop_counts = Counter(row["stop_reason"] for row in rows)
    overall = summarize_group(rows, label="all")
    overall["public_hidden_fail_given_total"] = overall["public_hidden_fail_total"]
    overall["public_hidden_fail_given_public_pass"] = overall[
        "public_hidden_fail_given_public_pass"
    ]
    overall["strict_suite_pass_note"] = "run_status == passed (historical suite leaderboard status)"
    overall["functional_pass_note"] = "evaluator scores.functional_gate == 1; includes valid submissions produced before step-limit exit"
    return {
        "schema_version": "featureliftbench.trajectory_statistics.v1",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "source_csv": str(input_path),
        "definitions": {
            "trajectory_inventory": "Every available experiments/python/openhands event trajectory; supplementary rows have analysis_included=false.",
            "primary_corpus": "Seven frozen official suites listed by build_trajectory_records.py; 450 analysis rows.",
            "public_hidden_fail": "public_pass=true and hidden_pass=false; skipped/unexecuted phases are NA.",
            "under_extraction_proxy": "extraction_ratio <= 0.25; footprint proxy, not a causal label.",
            "over_extraction_proxy": "extraction_ratio > 0.80; footprint proxy, not proof of literal copying.",
            "copied_file_count_and_loc": "Evaluator submission file_count/loc; submission-footprint proxy.",
            "repeated_file_reads": "Duplicate file_editor view actions to the same normalized path beyond the first.",
            "repeated_line_reads": "Duplicate view actions to the same normalized path and exact view_range beyond the first.",
        },
        "completeness": completeness(fieldnames, rows),
        "overall": overall,
        "by_model": grouped(rows, "model"),
        "by_split": grouped(rows, "split"),
        "by_task_type": grouped(rows, "task_type"),
        "by_dynamic_state": grouped(rows, "dynamic_state_task"),
        "extraction": extraction_summary(rows),
        "repeated_and_error_events": repeated_summary(rows),
        "error_sources": error_source_summary(rows),
        "primary_failure_counts": [
            {"primary_failure": key, **rate(value, total)}
            for key, value in primary_counts.most_common()
        ],
        "stop_reason_counts": [
            {"stop_reason": key, **rate(value, total)} for key, value in stop_counts.most_common()
        ],
        "cases": case_rows(rows),
    }


def md_table(headers: list[str], rows: Iterable[Iterable[Any]], aligns: list[str] | None = None) -> list[str]:
    align_values = aligns or ["---"] * len(headers)
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(align_values) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return lines


def render_group_table(groups: list[dict[str, Any]]) -> list[str]:
    return md_table(
        ["group", "runs", "suite pass", "functional pass", "public observed", "P→H fail / total", "env error", "median ratio", "median tokens"],
        (
            (
                f"`{group['label']}`",
                group["runs"],
                fmt_rate(group["strict_suite_pass"]),
                fmt_rate(group["functional_pass"]),
                fmt_rate(group["public_observed"]),
                fmt_rate(group["public_hidden_fail_total"]),
                fmt_rate(group["environment_error"]),
                "NA" if group["median_extraction_ratio"] is None else f"{group['median_extraction_ratio']:.3f}",
                "NA" if group["median_tokens"] is None else f"{group['median_tokens']:,.0f}",
            )
            for group in groups
        ),
        ["---", "---:", "---:", "---:", "---:", "---:", "---:", "---:", "---:"],
    )


def render_markdown(payload: dict[str, Any]) -> str:
    completeness_data = payload["completeness"]
    lines = [
        "# Trajectory statistics (generated)",
        "",
        f"Generated: `{payload['generated_at']}`",
        "",
        "This file is generated only from `trajectory_records.csv`; do not edit percentages here by hand.",
        "",
        (
            f"Inventory: {completeness_data.get('inventory_rows', completeness_data['rows'])} rows; "
            f"primary analysis: {completeness_data.get('analysis_rows', completeness_data['rows'])}; "
            f"excluded supplementary rows: {completeness_data.get('excluded_rows', 0)}."
        ),
        "",
        "## Overall",
        "",
    ]
    lines.extend(render_group_table([payload["overall"]]))
    lines.extend(["", "## By model", ""])
    lines.extend(render_group_table(payload["by_model"]))
    lines.extend(["", "## By split", ""])
    lines.extend(render_group_table(payload["by_split"]))
    lines.extend(["", "## By task type", ""])
    lines.extend(render_group_table(payload["by_task_type"]))

    lines.extend(["", "## Error-source separation", ""])
    error_rows = []
    for name, item in payload["error_sources"].items():
        metric = item.get("affected_runs") or item.get("all_runs")
        error_rows.append((f"`{name}`", fmt_rate(metric), item.get("events", "—"), item["definition"]))
    lines.extend(md_table(["source", "affected", "events", "definition"], error_rows))

    lines.extend(["", "## Primary failure labels", ""])
    lines.extend(
        md_table(
            ["label", "count / 450"],
            ((f"`{item['primary_failure']}`", fmt_rate(item)) for item in payload["primary_failure_counts"]),
        )
    )

    lines.extend(["", "## Extraction buckets", ""])
    extraction = payload["extraction"]
    bucket_rows = []
    for key in ("under_proxy_le_0_25", "middle_0_25_to_0_80", "over_proxy_gt_0_80"):
        group = extraction[key]
        bucket_rows.append(
            (
                f"`{key}`",
                group["runs"],
                fmt_rate(group["functional_pass"]),
                fmt_rate(group["public_hidden_fail_total"]),
                f"{group['median_extraction_ratio']:.3f}" if group["median_extraction_ratio"] is not None else "NA",
            )
        )
    lines.extend(md_table(["bucket", "known-ratio runs", "functional pass", "P→H fail", "median ratio"], bucket_rows))
    lines.extend(["", "### Under/over trajectory features", ""])
    lines.extend(
        md_table(
            ["bucket", "closure plan", "self tests", "hidden risk", "explicit finish", "repeat-read affected", "unsupported claim", "median files", "median tokens"],
            (
                (
                    f"`{key}`",
                    fmt_rate(extraction[key]["closure_plan_present"]),
                    fmt_rate(extraction[key]["self_generated_tests"]),
                    fmt_rate(extraction[key]["hidden_risk_discussed"]),
                    fmt_rate(extraction[key]["explicit_finish"]),
                    fmt_rate(extraction[key]["repeated_file_read_affected"]),
                    fmt_rate(extraction[key]["unsupported_completion_claim"]),
                    extraction[key]["median_copied_file_count"],
                    extraction[key]["median_tokens"],
                )
                for key in ("under_proxy_le_0_25", "over_proxy_gt_0_80")
            ),
        )
    )

    lines.extend(["", "## Repetition and error events", ""])
    lines.extend(
        md_table(
            ["metric", "affected runs", "event count", "median among affected"],
            (
                (
                    f"`{name}`",
                    fmt_rate(item["affected_runs"]),
                    item["event_count"],
                    item["median_among_affected"],
                )
                for name, item in payload["repeated_and_error_events"].items()
            ),
        )
    )

    lines.extend(["", "## Auditable cases", ""])
    lines.extend(
        md_table(
            ["task", "model", "public", "hidden", "ratio", "score", "files", "tokens", "stop", "primary failure", "evidence"],
            (
                (
                    f"`{case['task_id']}`",
                    f"`{case['model']}`",
                    case["public_pass"],
                    case["hidden_pass"],
                    "NA" if case["extraction_ratio"] is None else f"{case['extraction_ratio']:.3f}",
                    "NA" if case["final_score"] is None else f"{case['final_score']:.3f}",
                    case["copied_file_count"],
                    "NA" if case["tokens"] is None else f"{case['tokens']:,}",
                    case["stop_reason"],
                    f"`{case['primary_failure']}`",
                    "<br>".join(f"`{step}`" for step in case["evidence_step_ids"][:4]),
                )
                for case in payload["cases"]
            ),
        )
    )
    lines.append("")
    return "\n".join(lines)


def write_extremes(path: Path, rows: list[dict[str, str]]) -> None:
    keep = [
        row
        for row in rows
        if float_value(row["extraction_ratio"]) is not None
        and (float_value(row["extraction_ratio"]) <= 0.25 or float_value(row["extraction_ratio"]) > 0.80)
    ]
    fields = (
        "task_id",
        "run_id",
        "model",
        "task_type",
        "dynamic_state_task",
        "public_pass",
        "hidden_pass",
        "functional_pass",
        "extraction_ratio",
        "copied_file_count",
        "copied_loc",
        "repeated_file_reads",
        "repeated_line_reads",
        "tool_error_count",
        "harness_format_error_count",
        "closure_plan_present",
        "self_generated_tests",
        "hidden_risk_discussed",
        "stop_reason",
        "primary_failure",
        "trajectory_path",
        "evaluation_path",
        "evidence_step_ids",
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in sorted(keep, key=lambda r: (r["model"], float_value(r["extraction_ratio"]), r["task_id"])):
            writer.writerow({field: row[field] for field in fields})


def check_paths(rows: list[dict[str, str]], repo_root: Path) -> None:
    missing: list[str] = []
    for row in rows:
        for field, availability_field in (
            ("trajectory_path", "events_available"),
            ("evaluation_path", "evaluation_available"),
            ("run_path", None),
            ("metadata_path", None),
        ):
            value = row.get(field, "")
            if not value:
                continue
            expected = bool_value(row.get(availability_field, "")) if availability_field else True
            if expected and not (repo_root / value).exists():
                missing.append(f"{row['run_id']}::{field}::{value}")
    if missing:
        raise FileNotFoundError("CSV references absent files:\n" + "\n".join(missing[:50]))


def main() -> int:
    args = parse_args()
    fieldnames, inventory_rows = load_rows(args.input)
    if args.check_paths:
        check_paths(inventory_rows, Path(__file__).resolve().parents[2])
    rows = [
        row
        for row in inventory_rows
        if "analysis_included" not in row
        or bool_value(row.get("analysis_included", "")) is not False
    ]
    if not rows:
        raise ValueError("no rows are marked analysis_included=true")
    payload = build_payload(fieldnames, rows, args.input)
    inventory_completeness = completeness(fieldnames, inventory_rows)
    inventory_completeness.update(
        {
            "inventory_rows": len(inventory_rows),
            "analysis_rows": len(rows),
            "excluded_rows": len(inventory_rows) - len(rows),
            "exclusion_reasons": dict(
                sorted(
                    Counter(
                        row.get("exclusion_reason") or "unspecified"
                        for row in inventory_rows
                        if bool_value(row.get("analysis_included", "")) is False
                    ).items()
                )
            ),
        }
    )
    payload["completeness"] = inventory_completeness

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.write_text(render_markdown(payload), encoding="utf-8")
    write_extremes(args.output_extremes, rows)

    print(
        f"validated {len(inventory_rows)} unique inventory rows "
        f"({len(rows)} primary analysis rows) and {len(fieldnames)} columns"
    )
    print(f"wrote {args.output_json}")
    print(f"wrote {args.output_markdown}")
    print(f"wrote {args.output_extremes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
