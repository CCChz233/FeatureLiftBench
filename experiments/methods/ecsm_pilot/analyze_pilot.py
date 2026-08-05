#!/usr/bin/env python3
"""Analyze an ECSM pilot run into auditable per-cell and arm-level outputs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import statistics
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = REPO_ROOT / "tools" / "research_analysis"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))
HARNESS_DIR = REPO_ROOT / "harness"
if str(HARNESS_DIR) not in sys.path:
    sys.path.insert(0, str(HARNESS_DIR))

from build_trajectory_records import parse_event_features, phase_state  # noqa: E402
from featureliftbench.closure_gold import load_closure_gold  # noqa: E402
from featureliftbench.closure_gold import normalize_source_path as normalize_gold_source_path  # noqa: E402
from featureliftbench.closure_gold import score_closure  # noqa: E402
from featureliftbench.compactness import analyze_submission_footprint  # noqa: E402


CELL_FIELDS = (
    "pilot_id",
    "arm_id",
    "task_id",
    "seed",
    "scheduled",
    "run_available",
    "evaluation_available",
    "run_status",
    "build_pass",
    "public_pass",
    "hidden_pass",
    "functional_pass",
    "public_hidden_gap",
    "extraction_ratio",
    "final_score",
    "closure_precision",
    "closure_recall",
    "closure_f1",
    "closure_variant_id",
    "closure_gold_completeness",
    "closure_redundant_alternative_count",
    "closure_measurement",
    "closure_state_present",
    "gold_closure_size",
    "predicted_closure_size",
    "submitted_file_count",
    "copied_file_count",
    "copied_loc",
    "copied_fraction",
    "external_dependency_count",
    "unapproved_external_dependency_count",
    "path_leakage",
    "compactness_class",
    "total_tokens",
    "api_calls",
    "assistant_steps",
    "tool_calls",
    "repeated_file_reads",
    "repeated_line_reads",
    "repeated_terminal_commands",
    "repeated_exploration",
    "tool_error_count",
    "harness_format_error_count",
    "token_budget_exhausted",
    "run_path",
    "evaluation_path",
    "trajectory_path",
    "closure_state_path",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path(__file__).with_name("pilot_manifest.yaml"),
    )
    parser.add_argument("--run-root", type=Path, default=None)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "artifacts" / "research_analysis" / "ecsm_pilot",
    )
    parser.add_argument("--require-complete", action="store_true")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def bool_text(value: bool | None) -> str:
    if value is None:
        return ""
    return "true" if value else "false"


def number_text(value: int | float | None) -> str | int:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6f}"
    return value


def as_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return float(value)
    return None


def as_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def manifest_data(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("pilot manifest must be a mapping")
    return payload


def default_run_root(manifest: dict[str, Any]) -> Path:
    execution = manifest.get("execution") if isinstance(manifest.get("execution"), dict) else {}
    root = REPO_ROOT / str(execution.get("output_root") or "experiments/methods/ecsm_pilot/runs")
    root = root / str(manifest.get("pilot_id") or "ecsm-pilot")
    freeze_path = REPO_ROOT / str(execution.get("freeze_manifest") or "")
    if freeze_path.is_file():
        freeze = load_json(freeze_path)
        root = root / f"revision-{int(freeze.get('pilot_revision') or 0)}"
    return root


def manifest_cells(manifest: dict[str, Any]) -> list[tuple[str, str, int, Path]]:
    controls = manifest.get("controls") if isinstance(manifest.get("controls"), dict) else {}
    seeds = [int(value) for value in controls.get("seeds") or [0]]
    arms = [str(arm["id"]) for arm in manifest.get("arms") or [] if isinstance(arm, dict)]
    cells: list[tuple[str, str, int, Path]] = []
    for task in manifest.get("tasks") or []:
        if not isinstance(task, dict):
            continue
        task_id = str(task.get("task_id") or "")
        task_dir = REPO_ROOT / str(task.get("task_dir") or "")
        for seed in seeds:
            for arm in arms:
                cells.append((arm, task_id, seed, task_dir))
    return cells


def executable_gold_closure(task_dir: Path) -> set[str]:
    return load_closure_gold(task_dir).approved_artifact_values("file")


def normalize_source_path(raw: str, task_dir: Path) -> str | None:
    return normalize_gold_source_path(raw, task_dir)


def closure_state_candidates(cell_dir: Path) -> list[Path]:
    return [
        cell_dir / "workspace" / "ecsm_state.json",
        cell_dir / "workspace" / "closure_state.json",
        cell_dir / "agent" / "state" / "ecsm_state.json",
        cell_dir / "agent" / "state" / "dependency_manifest.json",
    ]


def state_predicted_closure(cell_dir: Path, task_dir: Path) -> tuple[set[str], Path | None]:
    for path in closure_state_candidates(cell_dir):
        data = load_json(path)
        if not data:
            continue
        raw_values: list[Any] = []
        for key in ("included_source_files", "runtime_files", "resource_files"):
            value = data.get(key)
            if isinstance(value, list):
                raw_values.extend(value)
        predicted = {
            normalized
            for value in raw_values
            if isinstance(value, str)
            if (normalized := normalize_source_path(value, task_dir)) is not None
        }
        if predicted:
            return predicted, path
    return set(), None


def normalized_code_lines(path: Path) -> set[str]:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return set()
    result = set()
    for line in lines:
        stripped = " ".join(line.strip().split())
        if not stripped or stripped.startswith("#"):
            continue
        result.add(stripped.replace("featurelifted.", ""))
    return result


def submission_dir(cell_dir: Path) -> Path | None:
    for candidate in (cell_dir / "submission", cell_dir / "workspace" / "submission"):
        if candidate.is_dir():
            return candidate
    return None


def provenance_predicted_closure(cell_dir: Path, task_dir: Path) -> set[str]:
    submission = submission_dir(cell_dir)
    repo_dir = task_dir / "repo"
    if submission is None or not repo_dir.is_dir():
        return set()
    source_files = [path for path in repo_dir.rglob("*") if path.is_file()]
    hash_index: defaultdict[str, list[Path]] = defaultdict(list)
    for path in source_files:
        try:
            hash_index[hashlib.sha256(path.read_bytes()).hexdigest()].append(path)
        except OSError:
            continue
    predicted: set[str] = set()
    unmatched_python: list[Path] = []
    for path in (candidate for candidate in submission.rglob("*") if candidate.is_file()):
        try:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            continue
        exact = hash_index.get(digest) or []
        if exact:
            predicted.add(exact[0].relative_to(task_dir).as_posix())
        elif path.suffix == ".py":
            unmatched_python.append(path)

    source_python = [(path, normalized_code_lines(path)) for path in source_files if path.suffix == ".py"]
    source_python = [(path, lines) for path, lines in source_python if len(lines) >= 5]
    for submitted in unmatched_python:
        submitted_lines = normalized_code_lines(submitted)
        if len(submitted_lines) < 5:
            continue
        best_path: Path | None = None
        best_score = 0.0
        for source_path, source_lines in source_python:
            intersection = len(submitted_lines & source_lines)
            containment = intersection / min(len(submitted_lines), len(source_lines))
            jaccard = intersection / len(submitted_lines | source_lines)
            score = 0.7 * containment + 0.3 * jaccard
            if score > best_score:
                best_score = score
                best_path = source_path
        if best_path is not None and best_score >= 0.55:
            predicted.add(best_path.relative_to(task_dir).as_posix())
    return predicted


def closure_metrics(cell_dir: Path, task_dir: Path) -> dict[str, Any]:
    gold = load_closure_gold(task_dir)
    predicted, state_path = state_predicted_closure(cell_dir, task_dir)
    measurement = "explicit_state" if predicted else ""
    if not predicted:
        predicted = provenance_predicted_closure(cell_dir, task_dir)
        measurement = "hash_or_line_provenance" if predicted else "unavailable"
    score = score_closure(gold, predicted, kind="file") if predicted else None
    if score is None:
        return {
            "precision": None,
            "recall": None,
            "f1": None,
            "variant_id": "",
            "gold_completeness": gold.completeness_for("file"),
            "redundant_alternative_count": None,
            "measurement": measurement,
            "state_path": state_path,
            "state_present": state_path is not None,
            "gold_size": len(gold.approved_artifact_values("file")),
            "predicted_size": len(predicted),
        }
    return {
        "precision": score.precision,
        "recall": score.recall,
        "f1": score.f1,
        "variant_id": score.variant_id,
        "gold_completeness": gold.completeness_for("file"),
        "redundant_alternative_count": score.redundant_alternative_count,
        "measurement": measurement,
        "state_path": state_path,
        "state_present": state_path is not None,
        "gold_size": score.required_requirement_count,
        "predicted_size": len(predicted),
    }


def build_cell_row(
    pilot_id: str,
    run_root: Path,
    arm_id: str,
    task_id: str,
    seed: int,
    task_dir: Path,
) -> dict[str, Any]:
    cell = run_root / arm_id / task_id / f"seed-{seed}"
    run_path = cell / "run.json"
    eval_path = cell / "eval" / "result.json"
    events_path = cell / "agent" / "openhands_events.jsonl"
    run = load_json(run_path)
    result = load_json(eval_path)
    event_features = parse_event_features(events_path, cell)
    closure = closure_metrics(cell, task_dir) if run else {
        "precision": None,
        "recall": None,
        "f1": None,
        "variant_id": "",
        "gold_completeness": load_closure_gold(task_dir).completeness_for("file"),
        "redundant_alternative_count": None,
        "measurement": "unavailable",
        "state_path": None,
        "state_present": False,
        "gold_size": len(executable_gold_closure(task_dir)),
        "predicted_size": 0,
    }

    scores = result.get("scores") if isinstance(result.get("scores"), dict) else {}
    metrics = result.get("metrics") if isinstance(result.get("metrics"), dict) else {}
    _, build_pass = phase_state(result.get("build"))
    _, public_pass = phase_state(result.get("public_tests"))
    _, hidden_pass = phase_state(result.get("hidden_tests"))
    functional_gate = as_float(scores.get("functional_gate"))
    functional_pass = functional_gate == 1.0 if functional_gate is not None else None
    submitted = submission_dir(cell)
    footprint = (
        analyze_submission_footprint(
            task_dir,
            submitted,
            functional_pass=functional_pass,
        )
        if submitted is not None and result
        else {}
    )

    agent = run.get("agent") if isinstance(run.get("agent"), dict) else {}
    usage = agent.get("usage") if isinstance(agent.get("usage"), dict) else {}
    if not usage:
        usage = load_json(cell / "agent" / "usage.json")
    raw_openhands_usage = load_json(cell / "agent" / "openhands_usage.json")

    repeated_exploration = (
        event_features.repeated_file_reads
        + event_features.repeated_line_reads
        + event_features.repeated_terminal_commands
    )
    return {
        "pilot_id": pilot_id,
        "arm_id": arm_id,
        "task_id": task_id,
        "seed": seed,
        "scheduled": True,
        "run_available": run_path.is_file(),
        "evaluation_available": eval_path.is_file(),
        "run_status": str(run.get("status") or "missing"),
        "build_pass": build_pass,
        "public_pass": public_pass,
        "hidden_pass": hidden_pass,
        "functional_pass": functional_pass,
        "public_hidden_gap": bool(public_pass is True and hidden_pass is False) if public_pass is not None and hidden_pass is not None else None,
        "extraction_ratio": as_float(scores.get("extraction_ratio")),
        "final_score": as_float(scores.get("final_score")),
        "closure_precision": closure["precision"],
        "closure_recall": closure["recall"],
        "closure_f1": closure["f1"],
        "closure_variant_id": closure["variant_id"],
        "closure_gold_completeness": closure["gold_completeness"],
        "closure_redundant_alternative_count": closure["redundant_alternative_count"],
        "closure_measurement": closure["measurement"],
        "closure_state_present": closure["state_present"],
        "gold_closure_size": closure["gold_size"],
        "predicted_closure_size": closure["predicted_size"],
        "submitted_file_count": footprint.get("submitted_file_count", as_int(metrics.get("file_count"))),
        "copied_file_count": footprint.get("copied_file_count"),
        "copied_loc": footprint.get("copied_loc"),
        "copied_fraction": footprint.get("copied_fraction"),
        "external_dependency_count": footprint.get("external_dependency_count"),
        "unapproved_external_dependency_count": footprint.get("unapproved_external_dependency_count"),
        "path_leakage": footprint.get("path_leakage"),
        "compactness_class": footprint.get("compactness_class", ""),
        "total_tokens": as_int(usage.get("total_tokens")),
        "api_calls": as_int(usage.get("api_calls")),
        "assistant_steps": as_int(usage.get("assistant_steps")),
        "tool_calls": event_features.tool_call_count,
        "repeated_file_reads": event_features.repeated_file_reads,
        "repeated_line_reads": event_features.repeated_line_reads,
        "repeated_terminal_commands": event_features.repeated_terminal_commands,
        "repeated_exploration": repeated_exploration,
        "tool_error_count": event_features.tool_error_count,
        "harness_format_error_count": event_features.harness_format_error_count,
        "token_budget_exhausted": bool(raw_openhands_usage.get("token_budget_exhausted")),
        "run_path": run_path.relative_to(REPO_ROOT).as_posix(),
        "evaluation_path": eval_path.relative_to(REPO_ROOT).as_posix(),
        "trajectory_path": events_path.relative_to(REPO_ROOT).as_posix(),
        "closure_state_path": closure["state_path"].relative_to(REPO_ROOT).as_posix() if closure["state_path"] else "",
    }


def csv_row(row: dict[str, Any]) -> dict[str, Any]:
    output = {}
    for key in CELL_FIELDS:
        value = row.get(key)
        if isinstance(value, bool) or value is None:
            output[key] = bool_text(value)
        else:
            output[key] = number_text(value)
    return output


def median(values: Iterable[int | float | None]) -> float | None:
    clean = [float(value) for value in values if value is not None]
    return statistics.median(clean) if clean else None


def mean(values: Iterable[int | float | None]) -> float | None:
    clean = [float(value) for value in values if value is not None]
    return statistics.fmean(clean) if clean else None


def arm_summary(rows: list[dict[str, Any]], arm_id: str) -> dict[str, Any]:
    arm_rows = [row for row in rows if row["arm_id"] == arm_id]
    evaluated = [row for row in arm_rows if row["evaluation_available"]]
    hidden_observed = [row for row in arm_rows if row["hidden_pass"] is not None]
    closure_observed = [row for row in arm_rows if row["closure_f1"] is not None]
    complete = bool(arm_rows) and len(evaluated) == len(arm_rows)
    return {
        "arm_id": arm_id,
        "scheduled": len(arm_rows),
        "evaluated": len(evaluated),
        "completion_rate": len(evaluated) / len(arm_rows) if arm_rows else None,
        "hidden_pass_itt": sum(row["hidden_pass"] is True for row in arm_rows) / len(arm_rows) if complete else None,
        "hidden_pass_observed": sum(row["hidden_pass"] is True for row in hidden_observed) / len(hidden_observed) if hidden_observed else None,
        "public_hidden_gap_itt": sum(row["public_hidden_gap"] is True for row in arm_rows) / len(arm_rows) if complete else None,
        "functional_pass_itt": sum(row["functional_pass"] is True for row in arm_rows) / len(arm_rows) if complete else None,
        "mean_closure_precision": mean(row["closure_precision"] for row in closure_observed),
        "mean_closure_recall": mean(row["closure_recall"] for row in closure_observed),
        "mean_closure_f1": mean(row["closure_f1"] for row in closure_observed),
        "closure_metric_coverage": len(closure_observed) / len(arm_rows) if arm_rows else None,
        "median_extraction_ratio": median(row["extraction_ratio"] for row in evaluated),
        "median_final_score": median(row["final_score"] for row in evaluated),
        "median_total_tokens": median(row["total_tokens"] for row in evaluated),
        "median_tool_calls": median(row["tool_calls"] for row in evaluated),
        "median_repeated_exploration": median(row["repeated_exploration"] for row in evaluated),
        "median_copied_file_count": median(row["copied_file_count"] for row in evaluated),
        "token_budget_exhausted": sum(row["token_budget_exhausted"] is True for row in arm_rows),
    }


def source_group_map(manifest: dict[str, Any]) -> dict[str, str]:
    selection = manifest.get("task_selection") if isinstance(manifest.get("task_selection"), dict) else {}
    path = REPO_ROOT / str(selection.get("source") or "")
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8", newline="") as handle:
        return {
            row["task_id"]: row.get("source_group_id") or row.get("source_repo") or row["task_id"]
            for row in csv.DictReader(handle)
        }


def clustered_hidden_summary(
    rows: list[dict[str, Any]],
    arm_id: str,
    groups: dict[str, str],
    *,
    seed: int,
    samples: int,
) -> dict[str, Any]:
    selected = [
        row for row in rows
        if row["arm_id"] == arm_id and row["hidden_pass"] is not None
    ]
    values = [1.0 if row["hidden_pass"] else 0.0 for row in selected]
    grouped: defaultdict[str, list[float]] = defaultdict(list)
    for row, value in zip(selected, values):
        grouped[groups.get(row["task_id"], row["task_id"])].append(value)
    group_means = [statistics.fmean(value) for value in grouped.values()]
    interval: list[float] = []
    if group_means and samples > 0:
        rng = random.Random(seed)
        for _ in range(samples):
            draw = [group_means[rng.randrange(len(group_means))] for _ in group_means]
            interval.append(statistics.fmean(draw))
        interval.sort()

    def percentile(fraction: float) -> float | None:
        if not interval:
            return None
        index = min(len(interval) - 1, max(0, round(fraction * (len(interval) - 1))))
        return interval[index]

    return {
        "arm_id": arm_id,
        "evaluated_task_count": len(selected),
        "source_group_count": len(grouped),
        "task_macro_hidden_pass": statistics.fmean(values) if values else None,
        "source_group_macro_hidden_pass": statistics.fmean(group_means) if group_means else None,
        "source_group_clustered_bootstrap_95ci": [percentile(0.025), percentile(0.975)],
        "bootstrap_samples": samples,
        "bootstrap_seed": seed,
    }


def paired_delta(rows: list[dict[str, Any]], treatment: str, control: str = "strong_prompt") -> dict[str, Any]:
    by_key = {(row["arm_id"], row["task_id"], row["seed"]): row for row in rows}
    pairs = []
    tasks = sorted({(row["task_id"], row["seed"]) for row in rows})
    for task_id, seed in tasks:
        left = by_key.get((treatment, task_id, seed))
        right = by_key.get((control, task_id, seed))
        if left is not None and right is not None and left["evaluation_available"] and right["evaluation_available"]:
            pairs.append((left, right))
    def delta(field: str) -> float | None:
        values = []
        for left, right in pairs:
            lvalue, rvalue = left.get(field), right.get(field)
            if isinstance(lvalue, bool):
                lvalue = 1.0 if lvalue else 0.0
            if isinstance(rvalue, bool):
                rvalue = 1.0 if rvalue else 0.0
            if isinstance(lvalue, (int, float)) and isinstance(rvalue, (int, float)):
                values.append(float(lvalue) - float(rvalue))
        return statistics.fmean(values) if values else None
    return {
        "treatment": treatment,
        "control": control,
        "paired_cells": len(pairs),
        "delta_hidden_pass": delta("hidden_pass"),
        "delta_public_hidden_gap": delta("public_hidden_gap"),
        "delta_final_score": delta("final_score"),
        "delta_extraction_ratio": delta("extraction_ratio"),
        "delta_closure_f1": delta("closure_f1"),
        "delta_total_tokens": delta("total_tokens"),
        "delta_tool_calls": delta("tool_calls"),
        "delta_repeated_exploration": delta("repeated_exploration"),
        "delta_copied_file_count": delta("copied_file_count"),
    }


def fmt(value: Any, percent: bool = False) -> str:
    if value is None:
        return "NA"
    if percent:
        return f"{float(value) * 100:.1f}%"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# ECSM pilot analysis (generated)",
        "",
        f"Pilot: `{payload['pilot_id']}`",
        f"Generated: `{payload['generated_at']}`",
        f"Completion: {payload['completed_cells']}/{payload['scheduled_cells']} cells",
        "",
        "Incomplete cells remain in the intention-to-treat denominator. Final/paper decision rules require the complete matrix; the separate four-task Stage-B rule is resource allocation only.",
        "",
        "## Arm summary",
        "",
        "| arm | evaluated | hidden ITT | P→H gap ITT | closure F1 | ratio | score | tokens | tools | repeated | files |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for arm in payload["arms"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{arm['arm_id']}`",
                    f"{arm['evaluated']}/{arm['scheduled']}",
                    fmt(arm["hidden_pass_itt"], True),
                    fmt(arm["public_hidden_gap_itt"], True),
                    fmt(arm["mean_closure_f1"]),
                    fmt(arm["median_extraction_ratio"]),
                    fmt(arm["median_final_score"]),
                    fmt(arm["median_total_tokens"]),
                    fmt(arm["median_tool_calls"]),
                    fmt(arm["median_repeated_exploration"]),
                    fmt(arm["median_copied_file_count"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Paired deltas versus Strong Prompt",
            "",
            "| treatment | pairs | Δhidden | Δgap | Δclosure F1 | Δscore | Δratio | Δtokens | Δtools |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for item in payload["paired_deltas"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{item['treatment']}`",
                    str(item["paired_cells"]),
                    fmt(item["delta_hidden_pass"]),
                    fmt(item["delta_public_hidden_gap"]),
                    fmt(item["delta_closure_f1"]),
                    fmt(item["delta_final_score"]),
                    fmt(item["delta_extraction_ratio"]),
                    fmt(item["delta_total_tokens"]),
                    fmt(item["delta_tool_calls"]),
                ]
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def stage_b_resource_decision(rows: list[dict[str, Any]], manifest: dict[str, Any]) -> dict[str, Any]:
    """Apply the preregistered 4-task gate for resource allocation only."""

    stages = manifest.get("stages") if isinstance(manifest.get("stages"), dict) else {}
    stage = stages.get("B") if isinstance(stages.get("B"), dict) else {}
    task_ids = {str(value) for value in stage.get("task_ids") or []}
    arm_ids = {str(value) for value in stage.get("arm_ids") or []}
    selected = [row for row in rows if row["task_id"] in task_ids and row["arm_id"] in arm_ids]
    complete = len(selected) == int(stage.get("expected_cells") or 20) and all(
        row["evaluation_available"] for row in selected
    )
    index = {(row["task_id"], row["seed"], row["arm_id"]): row for row in selected}

    def paired(treatment: str, control: str) -> dict[str, Any]:
        wins = losses = gap_reduction = 0
        closure_deltas: list[float] = []
        token_ratios: list[float] = []
        tool_ratios: list[float] = []
        pairs = 0
        for task_id in sorted(task_ids):
            left = index.get((task_id, 0, treatment))
            right = index.get((task_id, 0, control))
            if not left or not right:
                continue
            pairs += 1
            if left["hidden_pass"] is True and right["hidden_pass"] is False:
                wins += 1
            elif left["hidden_pass"] is False and right["hidden_pass"] is True:
                losses += 1
            if right["public_hidden_gap"] is True and left["public_hidden_gap"] is False:
                gap_reduction += 1
            if left["closure_f1"] is not None and right["closure_f1"] is not None:
                closure_deltas.append(float(left["closure_f1"]) - float(right["closure_f1"]))
            for key, target in (("total_tokens", token_ratios), ("tool_calls", tool_ratios)):
                lvalue = as_float(left.get(key))
                rvalue = as_float(right.get(key))
                if lvalue is not None and rvalue is not None and rvalue > 0:
                    target.append(lvalue / rvalue)
        return {
            "treatment": treatment,
            "control": control,
            "pairs": pairs,
            "hidden_wins": wins,
            "hidden_losses": losses,
            "public_hidden_gap_reductions": gap_reduction,
            "mean_closure_f1_delta": statistics.mean(closure_deltas) if closure_deltas else None,
            "median_token_ratio": statistics.median(token_ratios) if token_ratios else None,
            "median_tool_call_ratio": statistics.median(tool_ratios) if tool_ratios else None,
        }

    oracle = paired("oracle_closure", "oracle_locate")
    ecsm = paired("ecsm", "strong_prompt")
    oracle_hidden_gate = oracle["hidden_wins"] >= 2 and oracle["hidden_losses"] == 0
    oracle_closure_gate = (
        oracle["hidden_wins"] >= 1
        and oracle["hidden_losses"] == 0
        and oracle["mean_closure_f1_delta"] is not None
        and oracle["mean_closure_f1_delta"] >= 0.15
    )
    ecsm_gate = (
        ecsm["hidden_wins"] >= 2
        and ecsm["hidden_losses"] == 0
        and ecsm["public_hidden_gap_reductions"] >= 1
        and ecsm["median_token_ratio"] is not None
        and ecsm["median_tool_call_ratio"] is not None
        and ecsm["median_token_ratio"] <= 1.5
        and ecsm["median_tool_call_ratio"] <= 1.5
    )
    triggered = []
    if oracle_hidden_gate:
        triggered.append("oracle_closure_hidden")
    if oracle_closure_gate:
        triggered.append("oracle_closure_f1")
    if ecsm_gate:
        triggered.append("ecsm_prompt")
    return {
        "schema_version": "featureliftbench.ecsm_stage_b_resource_decision.v1",
        "purpose": "resource_allocation_only",
        "paper_conclusion_allowed": False,
        "stage_b_complete": complete,
        "continue_remaining_36": bool(complete and triggered),
        "triggered_gates": triggered,
        "oracle_closure_vs_locate": oracle,
        "ecsm_prompt_vs_strong_prompt": ecsm,
        "interpretation_constraint": (
            "Failure to trigger this four-task gate does not falsify any mechanism. "
            "Final claims require the complete Pilot, Diagnostic-40, and trajectory evidence."
        ),
    }


def main() -> int:
    args = parse_args()
    manifest = manifest_data(args.manifest.resolve())
    run_root = (args.run_root or default_run_root(manifest)).resolve()
    pilot_id = str(manifest.get("pilot_id") or "ecsm-pilot")
    cells = manifest_cells(manifest)
    rows = [
        build_cell_row(pilot_id, run_root, arm_id, task_id, seed, task_dir)
        for arm_id, task_id, seed, task_dir in cells
    ]
    completed = sum(row["evaluation_available"] for row in rows)
    if args.require_complete and completed != len(rows):
        raise RuntimeError(f"pilot matrix incomplete: {completed}/{len(rows)} evaluated")

    arm_ids = [str(arm["id"]) for arm in manifest.get("arms") or [] if isinstance(arm, dict)]
    analysis_config = manifest.get("analysis") if isinstance(manifest.get("analysis"), dict) else {}
    group_map = source_group_map(manifest)
    bootstrap_seed = int(analysis_config.get("bootstrap_seed") or 20260713)
    bootstrap_samples = int(analysis_config.get("bootstrap_samples") or 10000)
    payload = {
        "schema_version": "featureliftbench.ecsm_pilot_analysis.v1",
        "pilot_id": pilot_id,
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "manifest": args.manifest.resolve().as_posix(),
        "run_root": run_root.as_posix(),
        "scheduled_cells": len(rows),
        "completed_cells": completed,
        "arms": [arm_summary(rows, arm_id) for arm_id in arm_ids],
        "paired_deltas": [paired_delta(rows, arm_id) for arm_id in arm_ids if arm_id != "strong_prompt"],
        "macro_and_clustered_uncertainty": [
            clustered_hidden_summary(
                rows, arm_id, group_map,
                seed=bootstrap_seed + index,
                samples=bootstrap_samples,
            )
            for index, arm_id in enumerate(arm_ids)
        ],
        "closure_metric_note": (
            "Gold is loaded through the v1.1 requirement-group closure loader. Only complete file gold "
            "is scored; partial, legacy-unreviewed, or unresolved gold is NA. Predictions use explicit "
            "included_source_files when present, else conservative hash/line provenance."
        ),
    }
    resource_decision = stage_b_resource_decision(rows, manifest)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    records_path = args.output_dir / "pilot_records.csv"
    with records_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CELL_FIELDS)
        writer.writeheader()
        writer.writerows(csv_row(row) for row in rows)
    (args.output_dir / "pilot_summary.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.output_dir / "pilot_summary.md").write_text(render_markdown(payload), encoding="utf-8")
    (args.output_dir / "stage_b_resource_decision.json").write_text(
        json.dumps(resource_decision, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(rows)} scheduled cells ({completed} evaluated) to {records_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
