#!/usr/bin/env python3
"""Reproducible exploratory analysis for the frozen Python-150 results.

This analysis is intentionally separate from the Python-200' paper main table.
It reads the archived four-model Python-150 task-level results, validates their
grain, joins the frozen lift taxonomy, writes exact tables, and renders static
paper-oriented figures.
"""

from __future__ import annotations

import json
import math
import sqlite3
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import nbformat
import numpy as np
import pandas as pd
from scipy.stats import binomtest


REPORT_DIR = Path(__file__).resolve().parent
REPO_ROOT = REPORT_DIR.parents[2]
SOURCE_DIR = REPO_ROOT / "reports/paper_analysis/python150_with_deepseek150_20260805"
RESULTS_CSV = SOURCE_DIR / "metrics_task_results.csv"
RESULTS_MD = SOURCE_DIR / "RESULTS.md"
TAXONOMY_CSV = REPO_ROOT / "reports/lift_taxonomy/COVERAGE_TRIPLES.csv"
FIGURE_DIR = REPORT_DIR / "figures"
TABLE_DIR = REPORT_DIR / "tables"

MODEL_ORDER = [
    "deepseek/deepseek-v4-flash",
    "openai/Qwen3.5-122B-A10B-FP8",
    "openai/Qwen3.6-35B-A3B-FP8",
    "openai/gpt-oss-120b",
]
MODEL_LABELS = {
    "deepseek/deepseek-v4-flash": "DeepSeek V4 Flash",
    "openai/Qwen3.5-122B-A10B-FP8": "Qwen3.5 122B",
    "openai/Qwen3.6-35B-A3B-FP8": "Qwen3.6 35B",
    "openai/gpt-oss-120b": "GPT-OSS 120B",
}
SHORT_LABELS = {
    "DeepSeek V4 Flash": "DeepSeek",
    "Qwen3.5 122B": "Qwen3.5",
    "Qwen3.6 35B": "Qwen3.6",
    "GPT-OSS 120B": "GPT-OSS",
}
MODEL_COLORS = {
    "DeepSeek V4 Flash": "#3B6EA8",
    "Qwen3.5 122B": "#D49A2A",
    "Qwen3.6 35B": "#D97932",
    "GPT-OSS 120B": "#718355",
}
INK = "#20252B"
GRID = "#D9DEE5"


def _as_bool(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False)
    return series.astype(str).str.lower().eq("true")


def wilson_interval(successes: int, total: int, z: float = 1.95996398454) -> tuple[float, float]:
    if total == 0:
        return (0.0, 0.0)
    rate = successes / total
    denominator = 1 + z * z / total
    center = (rate + z * z / (2 * total)) / denominator
    half_width = z * math.sqrt(rate * (1 - rate) / total + z * z / (4 * total * total)) / denominator
    return center - half_width, center + half_width


def bootstrap_mean_interval(values: np.ndarray, seed: int, draws: int = 5000) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    if len(values) == 0:
        return (math.nan, math.nan)
    if len(values) == 1:
        return (float(values[0]), float(values[0]))
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(values), size=(draws, len(values)))
    means = values[indices].mean(axis=1)
    return tuple(np.quantile(means, [0.025, 0.975]).tolist())


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    results = pd.read_csv(RESULTS_CSV)
    bool_columns = [
        "functional_pass",
        "build_pass",
        "public_pass",
        "hidden_pass",
        "isolation_pass",
        "evaluation_present",
        "context_violation",
        "usage_unverified",
        "agent_passed",
        "agent_timed_out",
        "resource_limited",
    ]
    for column in bool_columns:
        results[column] = _as_bool(results[column])
    results["model_label"] = results["model"].map(MODEL_LABELS)
    results["model_short"] = results["model_label"].map(SHORT_LABELS)

    triple_rows: list[dict[str, object]] = []
    triples = pd.read_csv(TAXONOMY_CSV)
    for row in triples.itertuples(index=False):
        for task_id in str(row.task_ids).split(";"):
            triple_rows.append(
                {
                    "task_id": task_id,
                    "lift_type": row.lift_type,
                    "feature_family": row.feature_family,
                    "entanglement": row.entanglement,
                }
            )
    taxonomy = pd.DataFrame(triple_rows)
    return results, taxonomy


def validate_inputs(results: pd.DataFrame, taxonomy: pd.DataFrame) -> dict[str, object]:
    model_counts = results.groupby("model").size().reindex(MODEL_ORDER)
    evaluation_missing_by_model = (
        results.assign(missing=~results["evaluation_present"])
        .groupby("model_label")["missing"]
        .sum()
        .astype(int)
        .to_dict()
    )
    context_violations_by_model = (
        results.groupby("model_label")["context_violation"].sum().astype(int).to_dict()
    )
    key_columns = ["model", "task_id", "functional_pass"]
    quality = {
        "rows": int(len(results)),
        "models": int(results["model"].nunique()),
        "tasks": int(results["task_id"].nunique()),
        "rows_per_model": {MODEL_LABELS[k]: int(v) for k, v in model_counts.items()},
        "duplicate_model_task_pairs": int(results.duplicated(["model", "task_id"]).sum()),
        "null_key_cells": int(results[key_columns].isna().sum().sum()),
        "evaluation_missing_rows": int((~results["evaluation_present"]).sum()),
        "evaluation_missing_by_model": evaluation_missing_by_model,
        "token_complete_rows": int(
            results[["prompt_tokens", "completion_tokens", "total_tokens", "api_calls"]]
            .notna()
            .all(axis=1)
            .sum()
        ),
        "functional_pass_rows": int(results["functional_pass"].sum()),
        "pass_rows_with_rres": int(results.loc[results["functional_pass"], "extraction_ratio"].notna().sum()),
        "taxonomy_rows": int(len(taxonomy)),
        "taxonomy_unique_tasks": int(taxonomy["task_id"].nunique()),
        "taxonomy_duplicate_tasks": int(taxonomy["task_id"].duplicated().sum()),
        "taxonomy_join_coverage": int(results["task_id"].nunique() - len(set(results["task_id"]) - set(taxonomy["task_id"]))),
        "context_violation_rows": int(results["context_violation"].sum()),
        "context_violations_by_model": context_violations_by_model,
        "eligibility_caveat": (
            "Historical frozen Python-150 evidence only: evaluator image identity does not match the active "
            "paper freeze, and some runs violate the declared context allowance."
        ),
    }
    assert quality["rows"] == 600
    assert quality["models"] == 4
    assert quality["tasks"] == 150
    assert set(model_counts.tolist()) == {150}
    assert quality["duplicate_model_task_pairs"] == 0
    assert quality["null_key_cells"] == 0
    assert quality["token_complete_rows"] == 600
    assert quality["pass_rows_with_rres"] == quality["functional_pass_rows"]
    assert quality["taxonomy_unique_tasks"] == 150
    assert quality["taxonomy_duplicate_tasks"] == 0
    assert quality["taxonomy_join_coverage"] == 150
    return quality


def summarize(results: pd.DataFrame, taxonomy: pd.DataFrame) -> dict[str, pd.DataFrame]:
    model_rows: list[dict[str, object]] = []
    gate_rows: list[dict[str, object]] = []
    gate_columns = [
        ("Build", "build_pass"),
        ("Public", "public_pass"),
        ("Hidden", "hidden_pass"),
        ("Isolation", "isolation_pass"),
        ("Functional", "functional_pass"),
    ]
    for model in MODEL_ORDER:
        group = results.loc[results["model"].eq(model)].copy()
        label = MODEL_LABELS[model]
        successes = int(group["functional_pass"].sum())
        total = int(len(group))
        ci_low, ci_high = wilson_interval(successes, total)
        passing = group.loc[group["functional_pass"]]
        model_rows.append(
            {
                "model": label,
                "model_short": SHORT_LABELS[label],
                "assigned": total,
                "functional_pass": successes,
                "functional_rate": successes / total,
                "wilson_low": ci_low,
                "wilson_high": ci_high,
                "evaluation_missing": int((~group["evaluation_present"]).sum()),
                "context_violations": int(group["context_violation"].sum()),
                "run_status_passed": int(group["run_status"].eq("passed").sum()),
                "functional_despite_run_fail": int((group["functional_pass"] & ~group["run_status"].eq("passed")).sum()),
                "median_api_calls": float(group["api_calls"].median()),
                "mean_api_calls": float(group["api_calls"].mean()),
                "median_completion_tokens": float(group["completion_tokens"].median()),
                "agent_hours": float(group["agent_duration_seconds"].sum() / 3600),
                "pass_rres_median": float(passing["extraction_ratio"].median()),
                "pass_rres_q1": float(passing["extraction_ratio"].quantile(0.25)),
                "pass_rres_q3": float(passing["extraction_ratio"].quantile(0.75)),
                "pass_copy_fraction_median": float(passing["copied_fraction"].median()),
                "pass_copy_fraction_q1": float(passing["copied_fraction"].quantile(0.25)),
                "pass_copy_fraction_q3": float(passing["copied_fraction"].quantile(0.75)),
            }
        )
        for gate_order, (gate, column) in enumerate(gate_columns):
            passed = int(group[column].sum())
            gate_rows.append(
                {
                    "model": label,
                    "model_short": SHORT_LABELS[label],
                    "gate": gate,
                    "gate_order": gate_order,
                    "passed": passed,
                    "assigned": total,
                    "rate": passed / total,
                }
            )

    model_summary = pd.DataFrame(model_rows).sort_values("functional_rate", ascending=False)
    gate_summary = pd.DataFrame(gate_rows)

    pivot = (
        results.pivot(index="task_id", columns="model_label", values="functional_pass")
        .reindex(columns=[MODEL_LABELS[m] for m in MODEL_ORDER])
        .astype(bool)
    )
    pairwise_rows: list[dict[str, object]] = []
    labels = [MODEL_LABELS[m] for m in MODEL_ORDER]
    for left_index, left in enumerate(labels):
        for right in labels[left_index + 1 :]:
            both_pass = int((pivot[left] & pivot[right]).sum())
            left_only = int((pivot[left] & ~pivot[right]).sum())
            right_only = int((~pivot[left] & pivot[right]).sum())
            both_fail = int((~pivot[left] & ~pivot[right]).sum())
            discordant = left_only + right_only
            p_value = float(binomtest(left_only, discordant, 0.5).pvalue) if discordant else 1.0
            pairwise_rows.append(
                {
                    "left": left,
                    "right": right,
                    "pair": f"{SHORT_LABELS[left]} vs {SHORT_LABELS[right]}",
                    "both_pass": both_pass,
                    "left_only": left_only,
                    "right_only": right_only,
                    "both_fail": both_fail,
                    "discordant": discordant,
                    "left_advantage": left_only - right_only,
                    "mcnemar_exact_p": p_value,
                }
            )
    pairwise = pd.DataFrame(pairwise_rows)

    task_difficulty = pivot.copy()
    task_difficulty.columns = [SHORT_LABELS[column] for column in task_difficulty.columns]
    task_difficulty["models_solved"] = task_difficulty.sum(axis=1).astype(int)
    task_difficulty["solve_fraction"] = task_difficulty["models_solved"] / len(labels)
    task_difficulty = task_difficulty.join(taxonomy.set_index("task_id"), how="left").reset_index()

    lift_rows: list[dict[str, object]] = []
    family_rows: list[dict[str, object]] = []
    for seed, (lift_type, group) in enumerate(task_difficulty.groupby("lift_type", sort=True), start=100):
        ci_low, ci_high = bootstrap_mean_interval(group["solve_fraction"].to_numpy(), seed)
        lift_rows.append(
            {
                "lift_type": lift_type,
                "tasks": int(len(group)),
                "mean_models_solved": float(group["models_solved"].mean()),
                "mean_solve_fraction": float(group["solve_fraction"].mean()),
                "bootstrap_low": ci_low,
                "bootstrap_high": ci_high,
                "median_models_solved": float(group["models_solved"].median()),
            }
        )
    for seed, (family, group) in enumerate(task_difficulty.groupby("feature_family", sort=True), start=200):
        ci_low, ci_high = bootstrap_mean_interval(group["solve_fraction"].to_numpy(), seed)
        family_rows.append(
            {
                "feature_family": family,
                "tasks": int(len(group)),
                "mean_models_solved": float(group["models_solved"].mean()),
                "mean_solve_fraction": float(group["solve_fraction"].mean()),
                "bootstrap_low": ci_low,
                "bootstrap_high": ci_high,
                "median_models_solved": float(group["models_solved"].median()),
            }
        )
    lift_summary = pd.DataFrame(lift_rows).sort_values("mean_solve_fraction", ascending=False)
    family_summary = pd.DataFrame(family_rows).sort_values("mean_solve_fraction", ascending=False)

    solved_distribution = (
        task_difficulty.groupby(["lift_type", "models_solved"])
        .size()
        .rename("tasks")
        .reset_index()
    )
    complete_grid = pd.MultiIndex.from_product(
        [sorted(task_difficulty["lift_type"].unique()), range(5)],
        names=["lift_type", "models_solved"],
    )
    solved_distribution = (
        solved_distribution.set_index(["lift_type", "models_solved"])
        .reindex(complete_grid, fill_value=0)
        .reset_index()
    )
    solved_distribution["lift_total"] = solved_distribution.groupby("lift_type")["tasks"].transform("sum")
    solved_distribution["share"] = solved_distribution["tasks"] / solved_distribution["lift_total"]

    pass_rows = results.loc[results["functional_pass"]].copy()
    compactness_summary = model_summary[
        [
            "model",
            "functional_pass",
            "pass_rres_median",
            "pass_rres_q1",
            "pass_rres_q3",
            "pass_copy_fraction_median",
            "pass_copy_fraction_q1",
            "pass_copy_fraction_q3",
        ]
    ].copy()

    return {
        "model_summary": model_summary,
        "gate_summary": gate_summary,
        "pairwise_comparisons": pairwise,
        "task_difficulty": task_difficulty,
        "lift_type_summary": lift_summary,
        "feature_family_summary": family_summary,
        "solve_count_by_lift": solved_distribution,
        "compactness_summary": compactness_summary,
        "pass_rows": pass_rows,
    }


def configure_plot_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "axes.edgecolor": "#8A929C",
            "axes.linewidth": 0.8,
            "axes.titleweight": "semibold",
            "axes.titlecolor": INK,
            "text.color": INK,
            "axes.labelcolor": INK,
            "xtick.color": "#505963",
            "ytick.color": "#505963",
            "grid.color": GRID,
            "grid.linewidth": 0.7,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )


def save_figure(fig: plt.Figure, stem: str) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE_DIR / f"{stem}.png", dpi=220, bbox_inches="tight")
    fig.savefig(FIGURE_DIR / f"{stem}.pdf", bbox_inches="tight")
    plt.close(fig)


def plot_functional_pass(model_summary: pd.DataFrame) -> None:
    display_order = ["GPT-OSS 120B", "Qwen3.6 35B", "Qwen3.5 122B", "DeepSeek V4 Flash"]
    frame = model_summary.set_index("model").loc[display_order].reset_index()
    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    positions = np.arange(len(frame))
    colors = [MODEL_COLORS[m] for m in frame["model"]]
    ax.barh(positions, frame["functional_rate"] * 100, color=colors, edgecolor=INK, linewidth=0.5)
    errors = np.vstack(
        [
            (frame["functional_rate"] - frame["wilson_low"]) * 100,
            (frame["wilson_high"] - frame["functional_rate"]) * 100,
        ]
    )
    ax.errorbar(
        frame["functional_rate"] * 100,
        positions,
        xerr=errors,
        fmt="none",
        ecolor=INK,
        elinewidth=1.1,
        capsize=3,
    )
    for y, row in enumerate(frame.itertuples(index=False)):
        ax.text(
            row.wilson_high * 100 + 1.2,
            y,
            f"{row.functional_pass}/{row.assigned} ({row.functional_rate:.1%})",
            va="center",
            fontsize=9,
        )
    ax.set_yticks(positions, frame["model"])
    ax.set_xlim(0, 86)
    ax.set_xlabel("Functional Pass@1 (%)")
    ax.set_title("Functional Pass@1 on the frozen Python-150 suite")
    ax.grid(axis="x")
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    save_figure(fig, "fig01_functional_pass_ci")


def plot_gate_rates(gate_summary: pd.DataFrame) -> None:
    gate_order = ["Build", "Public", "Hidden", "Isolation", "Functional"]
    fig, ax = plt.subplots(figsize=(8.8, 5.4))
    base = np.arange(len(gate_order))
    offsets = np.linspace(-0.27, 0.27, 4)
    for offset, model in zip(offsets, [MODEL_LABELS[m] for m in MODEL_ORDER], strict=True):
        frame = gate_summary.loc[gate_summary["model"].eq(model)].set_index("gate").loc[gate_order]
        ax.scatter(
            frame["rate"] * 100,
            base + offset,
            s=62,
            color=MODEL_COLORS[model],
            edgecolor=INK,
            linewidth=0.5,
            label=model,
            zorder=3,
        )
    ax.set_yticks(base, gate_order)
    ax.invert_yaxis()
    ax.set_xlim(0, 105)
    ax.set_xlabel("Tasks passing gate (%)")
    ax.set_title("Independent evaluator-gate pass rates", pad=42)
    ax.grid(axis="x")
    ax.set_axisbelow(True)
    ax.legend(frameon=False, ncol=2, loc="lower center", bbox_to_anchor=(0.5, 1.03))
    ax.spines[["top", "right", "left"]].set_visible(False)
    save_figure(fig, "fig02_evaluator_gate_rates")


def plot_pairwise_advantage(pairwise: pd.DataFrame) -> None:
    labels = [MODEL_LABELS[m] for m in MODEL_ORDER]
    short = [SHORT_LABELS[label] for label in labels]
    matrix = np.zeros((len(labels), len(labels)), dtype=int)
    for row in pairwise.itertuples(index=False):
        left_index = labels.index(row.left)
        right_index = labels.index(row.right)
        matrix[left_index, right_index] = row.left_advantage
        matrix[right_index, left_index] = -row.left_advantage
    bound = max(abs(matrix.min()), abs(matrix.max()), 1)
    cmap = LinearSegmentedColormap.from_list("blue_white_orange", ["#3B6EA8", "#F7F7F5", "#D97932"])
    fig, ax = plt.subplots(figsize=(6.6, 5.6))
    image = ax.imshow(matrix, cmap=cmap, vmin=-bound, vmax=bound)
    for row_index in range(len(labels)):
        for column_index in range(len(labels)):
            value = matrix[row_index, column_index]
            ax.text(column_index, row_index, f"{value:+d}" if row_index != column_index else "—", ha="center", va="center", fontsize=10)
    ax.set_xticks(range(len(short)), short, rotation=25, ha="right")
    ax.set_yticks(range(len(short)), short)
    ax.set_xlabel("Column model")
    ax.set_ylabel("Row model")
    ax.set_title("Pairwise task advantage (row-only minus column-only passes)")
    colorbar = fig.colorbar(image, ax=ax, shrink=0.8)
    colorbar.set_label("Exclusive-pass difference")
    save_figure(fig, "fig03_pairwise_task_advantage")


def plot_solve_distribution(distribution: pd.DataFrame) -> None:
    lift_order = ["Composite", "Adapted", "Direct"]
    colors = ["#E7EBF0", "#B9CCE3", "#7599C3", "#D7A84A", "#D97932"]
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    left = np.zeros(len(lift_order))
    for solved_count, color in zip(range(5), colors, strict=True):
        values = (
            distribution.loc[distribution["models_solved"].eq(solved_count)]
            .set_index("lift_type")
            .reindex(lift_order)["share"]
            .fillna(0)
            .to_numpy()
        )
        ax.barh(lift_order, values * 100, left=left * 100, color=color, edgecolor="white", linewidth=0.8, label=str(solved_count))
        for row_index, value in enumerate(values):
            if value >= 0.085:
                ax.text((left[row_index] + value / 2) * 100, row_index, f"{value:.0%}", ha="center", va="center", fontsize=9)
        left += values
    task_counts = distribution.groupby("lift_type")["lift_total"].first().to_dict()
    for row_index, lift in enumerate(lift_order):
        ax.text(101, row_index, f"n={int(task_counts[lift])}", va="center", fontsize=9)
    ax.set_xlim(0, 108)
    ax.set_xlabel("Share of tasks (%)")
    ax.set_title("Number of models solving each task, by lift type")
    ax.legend(title="Models solved", frameon=False, ncol=5, loc="lower center", bbox_to_anchor=(0.5, 1.01))
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(False)
    save_figure(fig, "fig04_task_solve_count_by_lift")


def plot_efficiency(model_summary: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7.8, 5.4))
    for row in model_summary.itertuples(index=False):
        size = 80 + 8 * row.agent_hours
        ax.scatter(
            row.median_api_calls,
            row.functional_rate * 100,
            s=size,
            color=MODEL_COLORS[row.model],
            edgecolor=INK,
            linewidth=0.7,
            alpha=0.9,
        )
        x_offset = 1.4
        y_offset = 1.2 if row.model != "Qwen3.6 35B" else -3.0
        ax.text(row.median_api_calls + x_offset, row.functional_rate * 100 + y_offset, row.model, fontsize=9)
    ax.set_xlim(0, max(model_summary["median_api_calls"]) + 24)
    ax.set_ylim(0, 75)
    ax.set_xlabel("Median API calls per task")
    ax.set_ylabel("Functional Pass@1 (%)")
    ax.set_title("Functional performance and agent interaction volume")
    ax.grid(True)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    save_figure(fig, "fig05_pass_rate_vs_api_calls")


def plot_compactness(pass_rows: pd.DataFrame) -> None:
    labels = [MODEL_LABELS[m] for m in MODEL_ORDER]
    rres_values = [pass_rows.loc[pass_rows["model_label"].eq(label), "extraction_ratio"].dropna().to_numpy() for label in labels]
    copy_values = [pass_rows.loc[pass_rows["model_label"].eq(label), "copied_fraction"].dropna().to_numpy() for label in labels]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.6))
    for axis, values, title, xlabel in [
        (axes[0], rres_values, "Reference-relative extraction size among passes", "Submitted LOC / reference LOC (log scale)"),
        (axes[1], copy_values, "Copied fraction among passes", "Heuristic copied-code fraction"),
    ]:
        box = axis.boxplot(values, vert=False, tick_labels=labels, patch_artist=True, showfliers=False, widths=0.55)
        for patch, label in zip(box["boxes"], labels, strict=True):
            patch.set_facecolor(MODEL_COLORS[label])
            patch.set_alpha(0.65)
            patch.set_edgecolor(INK)
        for median in box["medians"]:
            median.set_color(INK)
            median.set_linewidth(1.5)
        axis.set_title(title)
        axis.set_xlabel(xlabel)
        axis.grid(axis="x")
        axis.set_axisbelow(True)
        axis.spines[["top", "right", "left"]].set_visible(False)
    axes[0].set_xscale("log")
    axes[0].axvline(1.0, color=INK, linestyle="--", linewidth=1.0, label="Reference size")
    axes[0].legend(frameon=False, loc="lower right")
    axes[1].set_xlim(0, 1.03)
    fig.suptitle("Compactness diagnostics are conditioned on Functional Pass", fontsize=13, fontweight="semibold")
    fig.tight_layout()
    save_figure(fig, "fig06_pass_conditioned_compactness")


def plot_feature_family(family_summary: pd.DataFrame) -> None:
    frame = family_summary.sort_values("mean_solve_fraction", ascending=True).reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(9.2, 6.8))
    positions = np.arange(len(frame))
    errors = np.vstack(
        [
            frame["mean_solve_fraction"] - frame["bootstrap_low"],
            frame["bootstrap_high"] - frame["mean_solve_fraction"],
        ]
    )
    ax.errorbar(
        frame["mean_solve_fraction"] * 100,
        positions,
        xerr=errors * 100,
        fmt="o",
        markersize=7,
        color="#3B6EA8",
        ecolor="#7D9FC7",
        elinewidth=1.4,
        capsize=3,
    )
    for y, row in enumerate(frame.itertuples(index=False)):
        ax.text(min(row.bootstrap_high * 100 + 2.2, 102), y, f"n={row.tasks}", va="center", fontsize=8.5)
    ax.set_yticks(positions, frame["feature_family"].str.replace("_", " "))
    ax.set_xlim(0, 110)
    ax.set_xlabel("Mean share of four models solving a task (%)")
    ax.set_title("Cross-model task solvability by feature family")
    ax.grid(axis="x")
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    save_figure(fig, "fig07_feature_family_solvability")


def render_figures(tables: dict[str, pd.DataFrame]) -> None:
    configure_plot_style()
    plot_functional_pass(tables["model_summary"])
    plot_gate_rates(tables["gate_summary"])
    plot_pairwise_advantage(tables["pairwise_comparisons"])
    plot_solve_distribution(tables["solve_count_by_lift"])
    plot_efficiency(tables["model_summary"])
    plot_compactness(tables["pass_rows"])
    plot_feature_family(tables["feature_family_summary"])


def dataframe_records(frame: pd.DataFrame) -> list[dict[str, object]]:
    clean = frame.replace({np.nan: None, np.inf: None, -np.inf: None})
    return json.loads(clean.to_json(orient="records"))


def build_artifact(quality: dict[str, object], tables: dict[str, pd.DataFrame]) -> dict[str, object]:
    source_results = {
        "id": "python150-results",
        "label": "Frozen Python-150 task-level results",
        "path": "reports/paper_analysis/python150_with_deepseek150_20260805/metrics_task_results.csv",
        "query": {
            "description": "Reproducible Python aggregation over 600 model-task result rows.",
            "engine": "python/pandas",
            "language": "python",
            "sql": "SELECT * FROM results ORDER BY model_label, task_id",
            "executed_at": "2026-08-30",
            "tables_used": ["metrics_task_results.csv"],
            "filters": ["Frozen Python-150 only", "Four OpenHands model configurations", "Functional Pass@1 from evaluator gates"],
            "metric_definitions": [
                "Functional Pass@1 = build AND public AND hidden AND isolation gates.",
                "Wilson 95% intervals use the assigned 150-task denominator per model.",
                "Compactness summaries include only functionally passing submissions.",
            ],
        },
    }
    source_taxonomy = {
        "id": "python150-taxonomy",
        "label": "Frozen Python-150 lift taxonomy",
        "path": "reports/lift_taxonomy/COVERAGE_TRIPLES.csv",
        "query": {
            "description": "Task-level lift type and feature-family labels joined by task_id.",
            "engine": "python/pandas",
            "language": "python",
            "sql": "SELECT * FROM taxonomy ORDER BY task_id",
            "executed_at": "2026-08-30",
            "tables_used": ["COVERAGE_TRIPLES.csv"],
            "filters": ["150 task IDs present in the result matrix"],
            "metric_definitions": [
                "Task solvability = number of the four evaluated models that functionally pass a task, divided by four.",
                "Bootstrap intervals resample tasks within each family or lift type.",
            ],
        },
    }
    model_table = tables["model_summary"].copy()
    model_table["wilson_95"] = model_table.apply(lambda row: f"{row.wilson_low:.1%}–{row.wilson_high:.1%}", axis=1)

    def table_source(table_name: str, label: str, metric_definitions: list[str]) -> dict[str, object]:
        return {
            "id": f"python150-{table_name}",
            "label": label,
            "path": "reports/paper_analysis/python150_exploratory_20260830/analysis.sqlite",
            "query": {
                "description": f"Read the verified {table_name} analysis table.",
                "engine": "sqlite",
                "language": "sql",
                "executed_at": "2026-08-30",
                "sql": f"SELECT * FROM {table_name}",
                "tables_used": [f"analysis.sqlite.{table_name}"],
                "filters": ["Frozen Python-150 exploratory analysis"],
                "metric_definitions": metric_definitions,
            },
        }

    artifact = {
        "surface": "report",
        "manifest": {
            "version": 1,
            "surface": "report",
            "title": "Frozen Python-150 Benchmark Results: Exploratory Analysis",
            "description": "Four-model capability, failure-depth, task-difficulty, efficiency, and compactness analysis.",
            "generatedAt": "2026-08-30",
            "sources": [source_results, source_taxonomy],
            "blocks": [
                {"id": "title", "type": "markdown", "body": "# Frozen Python-150 Benchmark Results: Exploratory Analysis"},
                {
                    "id": "technical-summary",
                    "type": "markdown",
                    "body": (
                        "## Technical summary\n\n"
                        "DeepSeek V4 Flash records 99/150 Functional passes (66.0%), while Qwen3.5 and Qwen3.6 each record 59/150 (39.3%) and GPT-OSS records 27/150 (18.0%). "
                        "The aggregate Qwen tie hides 40 task-level disagreements. Across all models, 42 tasks are solved by none and 11 by all four. "
                        "These results are useful for exploratory benchmark analysis but are not eligible for the final Python-200′ main table because evaluator-image identity and context-policy checks remain unresolved."
                    ),
                },
                {
                    "id": "capability-section",
                    "type": "markdown",
                    "body": (
                        "## DeepSeek leads the four-model comparison\n\n"
                        "The chart reports the evaluator-defined Functional Pass@1 rate with Wilson 95% intervals. DeepSeek's interval is separated from both Qwen configurations; GPT-OSS is lower still. The comparison describes complete model–OpenHands configurations, not base models in isolation."
                    ),
                },
                {"id": "functional-chart-block", "type": "chart", "chartId": "functional-chart"},
                {"id": "model-table-block", "type": "table", "tableId": "model-table"},
                {
                    "id": "gates-section",
                    "type": "markdown",
                    "body": (
                        "## Public and Hidden behavior create the largest separation\n\n"
                        "Build and isolation are comparatively high for every model. The largest capability spread appears at Public and Hidden behavior, which is consistent with contract-completion and generalization failures rather than packaging alone. Gate rates are shown independently; they should not be read as a strictly nested funnel."
                    ),
                },
                {"id": "gate-chart-block", "type": "chart", "chartId": "gate-chart"},
                {
                    "id": "task-section",
                    "type": "markdown",
                    "body": (
                        "## Aggregate ties conceal complementary successes\n\n"
                        "Qwen3.5 and Qwen3.6 have the same 59/150 aggregate score, yet each exclusively passes 20 tasks. Task-level paired comparisons are therefore more informative than ranking equal totals alone. DeepSeek exclusively passes 46 tasks against either Qwen, while each Qwen exclusively passes six against DeepSeek."
                    ),
                },
                {"id": "pairwise-table-block", "type": "table", "tableId": "pairwise-table"},
                {
                    "id": "difficulty-section",
                    "type": "markdown",
                    "body": (
                        "## Composite and resource-heavy tasks remain the least solved\n\n"
                        "Direct tasks are solved by an average of 2.20 of four models, compared with 1.36 for Adapted and 1.00 for Composite tasks. Family-level results are descriptive: task selection is not random, labels are AI-assisted, and the bootstrap intervals quantify variation across the observed tasks rather than population uncertainty."
                    ),
                },
                {"id": "lift-chart-block", "type": "chart", "chartId": "lift-chart"},
                {"id": "family-table-block", "type": "table", "tableId": "family-table"},
                {
                    "id": "compactness-section",
                    "type": "markdown",
                    "body": (
                        "## Higher correctness does not imply compact extraction\n\n"
                        "Among functionally passing submissions, DeepSeek has a median reference-relative extraction size of 0.985 and a median copied fraction of 0.970. GPT-OSS passes fewer tasks but has a lower median copied fraction of 0.269. These pass-conditioned summaries describe different survivor sets and must not be interpreted as an unconditional compactness ranking."
                    ),
                },
                {"id": "compactness-table-block", "type": "table", "tableId": "compactness-table"},
                {
                    "id": "scope-section",
                    "type": "markdown",
                    "body": (
                        "## Scope, definitions, and methodology\n\n"
                        "The analysis covers 600 unique model-task pairs: four OpenHands configurations evaluated on the same 150 frozen tasks. Functional Pass@1 is the conjunction of build, Public, Hidden, and isolation gates. Wilson intervals use the 150-task denominator. Pairwise differences use exact McNemar tests; family and lift-type intervals bootstrap tasks. Missing evaluator records are counted as non-passes, matching the archived result contract."
                    ),
                },
                {
                    "id": "limitations-section",
                    "type": "markdown",
                    "body": (
                        "## Limitations and robustness\n\n"
                        f"The data matrix has no duplicate model-task pairs and complete token records, but {quality['evaluation_missing_rows']} rows lack evaluator output and {quality['context_violation_rows']} rows violate the declared context allowance. The archived evaluator image also differs from the active paper freeze. Consequently, this report is suitable for exploratory analysis and figure development, not the final Python-200′ leaderboard or a causal claim about task attributes."
                    ),
                },
                {
                    "id": "next-steps-section",
                    "type": "markdown",
                    "body": (
                        "## Recommended next steps\n\n"
                        "1. Reuse the figure specifications, but replace the result matrix with fully eligible Python-200′ runs.\n"
                        "2. Preserve paired task-level comparisons and split compactness by Python-150 versus Hard-50.\n"
                        "3. Audit the AI-assisted taxonomy labels before presenting family differences as a primary empirical claim."
                    ),
                },
                {
                    "id": "questions-section",
                    "type": "markdown",
                    "body": (
                        "## Further questions\n\n"
                        "- Do the task-level model disagreements persist on the Hard-50 split?\n"
                        "- Which contract-closure symptoms explain the 42 tasks solved by no model?\n"
                        "- Does compactness remain model-dependent after conditioning on the same paired passing tasks?"
                    ),
                },
            ],
            "charts": [
                {
                    "id": "functional-chart",
                    "type": "bar",
                    "title": "Functional Pass@1 by model",
                    "description": "Frozen Python-150; 150 assigned tasks per model.",
                    "dataset": "model_summary",
                    "encodings": {
                        "x": {"field": "model", "type": "nominal", "title": "Model"},
                        "y": {"field": "functional_rate", "type": "quantitative", "title": "Functional Pass@1", "format": "percent"},
                    },
                    "options": {"orientation": "vertical", "valueLabels": True},
                    "source": table_source(
                        "model_summary",
                        "Python-150 model summary",
                        ["Functional rate = functionally passing tasks / 150 assigned tasks."],
                    ),
                },
                {
                    "id": "gate-chart",
                    "type": "bar",
                    "title": "Evaluator-gate pass rates",
                    "description": "Independent gate rates over the same 150 assigned tasks per model.",
                    "dataset": "gate_summary",
                    "encodings": {
                        "x": {"field": "gate", "type": "nominal", "title": "Gate"},
                        "y": {"field": "rate", "type": "quantitative", "title": "Pass rate", "format": "percent"},
                        "color": {"field": "model_short", "type": "nominal", "title": "Model"},
                    },
                    "options": {"orientation": "vertical", "grouping": "grouped", "legend": True},
                    "source": table_source(
                        "gate_summary",
                        "Python-150 evaluator-gate summary",
                        ["Gate rate = tasks passing the named evaluator gate / 150 assigned tasks."],
                    ),
                },
                {
                    "id": "lift-chart",
                    "type": "bar",
                    "title": "Mean task solvability by lift type",
                    "description": "Mean share of the four models solving each task; task counts retained in the dataset.",
                    "dataset": "lift_type_summary",
                    "encodings": {
                        "x": {"field": "lift_type", "type": "nominal", "title": "Lift type"},
                        "y": {"field": "mean_solve_fraction", "type": "quantitative", "title": "Mean share of models solving", "format": "percent"},
                    },
                    "options": {"orientation": "vertical", "valueLabels": True},
                    "source": table_source(
                        "lift_type_summary",
                        "Python-150 lift-type solvability summary",
                        ["Mean solve fraction averages task-level models_solved / 4 within each lift type."],
                    ),
                },
            ],
            "tables": [
                {
                    "id": "model-table",
                    "title": "Model-level functional results and audit fields",
                    "description": "Exact values over 150 assigned tasks per model.",
                    "dataset": "model_table",
                    "columns": [
                        {"field": "model", "label": "Model", "type": "text"},
                        {"field": "functional_pass", "label": "Pass", "type": "number"},
                        {"field": "assigned", "label": "Assigned", "type": "number"},
                        {"field": "functional_rate", "label": "Rate", "type": "percent"},
                        {"field": "wilson_95", "label": "Wilson 95%", "type": "text"},
                        {"field": "context_violations", "label": "Context violations", "type": "number"},
                    ],
                    "defaultSort": {"field": "functional_rate", "direction": "desc"},
                    "source": table_source(
                        "model_table",
                        "Python-150 exact model table",
                        ["Wilson 95% is computed from the assigned 150-task denominator."],
                    ),
                },
                {
                    "id": "pairwise-table",
                    "title": "Exact paired task comparisons",
                    "description": "Left-only and right-only passes over the same 150 task IDs.",
                    "dataset": "pairwise_comparisons",
                    "columns": [
                        {"field": "pair", "label": "Pair", "type": "text"},
                        {"field": "both_pass", "label": "Both pass", "type": "number"},
                        {"field": "left_only", "label": "Left only", "type": "number"},
                        {"field": "right_only", "label": "Right only", "type": "number"},
                        {"field": "both_fail", "label": "Both fail", "type": "number"},
                        {"field": "mcnemar_exact_p", "label": "Exact p", "type": "number"},
                    ],
                    "defaultSort": {"field": "mcnemar_exact_p", "direction": "asc"},
                    "source": table_source(
                        "pairwise_comparisons",
                        "Python-150 paired comparisons",
                        ["Exact p is a two-sided exact McNemar test over discordant task outcomes."],
                    ),
                },
                {
                    "id": "family-table",
                    "title": "Feature-family task solvability",
                    "description": "Observed Python-150 tasks; bootstrap intervals resample tasks within family.",
                    "dataset": "feature_family_summary",
                    "columns": [
                        {"field": "feature_family", "label": "Feature family", "type": "text"},
                        {"field": "tasks", "label": "Tasks", "type": "number"},
                        {"field": "mean_models_solved", "label": "Mean models solved", "type": "number"},
                        {"field": "mean_solve_fraction", "label": "Solve fraction", "type": "percent"},
                        {"field": "bootstrap_low", "label": "CI low", "type": "percent"},
                        {"field": "bootstrap_high", "label": "CI high", "type": "percent"},
                    ],
                    "defaultSort": {"field": "mean_solve_fraction", "direction": "asc"},
                    "source": table_source(
                        "feature_family_summary",
                        "Python-150 feature-family summary",
                        ["Bootstrap intervals resample tasks within each observed feature family."],
                    ),
                },
                {
                    "id": "compactness-table",
                    "title": "Pass-conditioned compactness summaries",
                    "description": "Medians and interquartile ranges among functionally passing submissions only.",
                    "dataset": "compactness_summary",
                    "columns": [
                        {"field": "model", "label": "Model", "type": "text"},
                        {"field": "functional_pass", "label": "Passing tasks", "type": "number"},
                        {"field": "pass_rres_median", "label": "Median RRES", "type": "number"},
                        {"field": "pass_rres_q1", "label": "RRES Q1", "type": "number"},
                        {"field": "pass_rres_q3", "label": "RRES Q3", "type": "number"},
                        {"field": "pass_copy_fraction_median", "label": "Median copied fraction", "type": "percent"},
                    ],
                    "defaultSort": {"field": "functional_pass", "direction": "desc"},
                    "source": table_source(
                        "compactness_summary",
                        "Python-150 pass-conditioned compactness summary",
                        ["RRES and copied fraction are summarized only among functionally passing submissions."],
                    ),
                },
            ],
        },
        "snapshot": {
            "version": 1,
            "status": "ready",
            "generatedAt": "2026-08-30",
            "datasets": {
                "model_summary": dataframe_records(tables["model_summary"]),
                "model_table": dataframe_records(model_table),
                "gate_summary": dataframe_records(tables["gate_summary"]),
                "pairwise_comparisons": dataframe_records(tables["pairwise_comparisons"]),
                "lift_type_summary": dataframe_records(tables["lift_type_summary"]),
                "feature_family_summary": dataframe_records(tables["feature_family_summary"]),
                "compactness_summary": dataframe_records(tables["compactness_summary"]),
            },
        },
        "sources": [source_results, source_taxonomy],
    }
    return artifact


def write_chart_map() -> None:
    chart_map = """# Python-150 chart map

| Figure | Analytical question | Family / form | Supported claim | Required caveat |
| --- | --- | --- | --- | --- |
| `fig01_functional_pass_ci` | How do the four configurations compare on Functional Pass@1? | Horizontal bar + Wilson interval | DeepSeek leads; the Qwen configurations tie in aggregate; GPT-OSS is lower | Historical Python-150 evidence; configuration-level result |
| `fig02_evaluator_gate_rates` | At which evaluator gates do models separate? | Grouped dot plot | Most separation appears at Public and Hidden behavior | Gates are independent indicators, not a causal funnel |
| `fig03_pairwise_task_advantage` | Do equal totals hide task-level differences? | Diverging matrix | Qwen3.5 and Qwen3.6 trade 20 exclusive passes each | Pairwise difference is descriptive; exact tests are in the table |
| `fig04_task_solve_count_by_lift` | How many models solve tasks of each lift type? | 100% stacked bar | Direct tasks are more broadly solved; Composite tasks concentrate unsolved cases | Task selection is non-random; labels are AI-assisted |
| `fig05_pass_rate_vs_api_calls` | How does capability relate to interaction volume? | Labeled scatter | Higher interaction volume does not uniquely determine success | Four intentionally labeled configurations; descriptive only |
| `fig06_pass_conditioned_compactness` | Are correct packages compact? | Two-panel box plot | Correctness and compactness are distinct; DeepSeek passes are often copy-heavy | Survivor sets differ by model; copied fraction is heuristic |
| `fig07_feature_family_solvability` | Which feature families are least broadly solved? | Dot + task-bootstrap interval | Resource, validation, and registry families are less broadly solved in this sample | Multiple descriptive cuts; not a causal difficulty estimate |
"""
    (REPORT_DIR / "chart_map.md").write_text(chart_map, encoding="utf-8")


def write_notebook(quality: dict[str, object], tables: dict[str, pd.DataFrame]) -> None:
    notebook = nbformat.v4.new_notebook()
    notebook["metadata"]["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    notebook["cells"] = [
        nbformat.v4.new_markdown_cell(
            "# Frozen Python-150 exploratory analysis\n\n"
            "## tl;dr\n\n"
            "- DeepSeek V4 Flash: **99/150 (66.0%)** Functional Pass@1.\n"
            "- Qwen3.5 and Qwen3.6: **59/150 (39.3%)** each, but they disagree on 40 task outcomes.\n"
            "- GPT-OSS: **27/150 (18.0%)**.\n"
            "- **42 tasks** are solved by no evaluated model; **11 tasks** are solved by all four.\n"
            "- This is historical Python-150 evidence with evaluator-image and context-policy caveats, not the final Python-200′ leaderboard."
        ),
        nbformat.v4.new_markdown_cell(
            "## Context & Methods\n\n"
            "The notebook reruns the checked analysis module. Functional Pass@1 is the conjunction of build, Public, Hidden, and isolation gates. Wilson intervals use the 150-task denominator; paired model comparisons use exact McNemar tests; task-family intervals bootstrap tasks."
        ),
        nbformat.v4.new_code_cell(
            "from pathlib import Path\n"
            "import sys\n"
            "REPORT_DIR = Path.cwd()\n"
            "sys.path.insert(0, str(REPORT_DIR))\n"
            "from analyze_python150 import run_analysis\n"
            "outputs = run_analysis(write_notebook_file=False)\n"
            "quality = outputs['quality']\n"
            "tables = outputs['tables']\n"
            "quality"
        ),
        nbformat.v4.new_markdown_cell("## Data\n\nThe source has 600 unique model-task rows, exactly 150 tasks per model, with no duplicate model-task keys."),
        nbformat.v4.new_code_cell(
            "tables['model_summary'][['model','functional_pass','assigned','functional_rate','wilson_low','wilson_high','context_violations','evaluation_missing']]"
        ),
        nbformat.v4.new_markdown_cell("## Results\n\n### Functional capability and paired comparisons"),
        nbformat.v4.new_code_cell("tables['pairwise_comparisons']"),
        nbformat.v4.new_code_cell(
            "from IPython.display import display, Image\n"
            "for name in ['fig01_functional_pass_ci','fig02_evaluator_gate_rates','fig03_pairwise_task_advantage']:\n"
            "    display(Image(filename=str(REPORT_DIR / 'figures' / f'{name}.png'), width=850))"
        ),
        nbformat.v4.new_markdown_cell("### Task difficulty, efficiency, and compactness"),
        nbformat.v4.new_code_cell("tables['lift_type_summary']"),
        nbformat.v4.new_code_cell("tables['feature_family_summary']"),
        nbformat.v4.new_code_cell(
            "for name in ['fig04_task_solve_count_by_lift','fig05_pass_rate_vs_api_calls','fig06_pass_conditioned_compactness','fig07_feature_family_solvability']:\n"
            "    display(Image(filename=str(REPORT_DIR / 'figures' / f'{name}.png'), width=900))"
        ),
        nbformat.v4.new_markdown_cell(
            "## Takeaways\n\n"
            "1. Functional capability differs substantially across the four model–runtime configurations.\n"
            "2. Public and Hidden behavior, not buildability alone, account for most of the separation.\n"
            "3. Equal aggregate scores can hide substantial task-level complementarity.\n"
            "4. Direct tasks are more broadly solved than Adapted or Composite tasks in the observed suite.\n"
            "5. Compactness must be reported after Functional Pass and on paired survivor sets where possible."
        ),
    ]
    nbformat.write(notebook, REPORT_DIR / "python150_analysis.ipynb")


def write_outputs(quality: dict[str, object], tables: dict[str, pd.DataFrame]) -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    for name, frame in tables.items():
        if name == "pass_rows":
            continue
        frame.to_csv(TABLE_DIR / f"{name}.csv", index=False)
    results, taxonomy = load_inputs()
    sqlite_path = REPORT_DIR / "analysis.sqlite"
    with sqlite3.connect(sqlite_path) as connection:
        results.to_sql("results", connection, if_exists="replace", index=False)
        taxonomy.to_sql("taxonomy", connection, if_exists="replace", index=False)
        for name, frame in tables.items():
            if name == "pass_rows":
                continue
            frame.to_sql(name, connection, if_exists="replace", index=False)
        model_table = tables["model_summary"].copy()
        model_table["wilson_95"] = model_table.apply(
            lambda row: f"{row.wilson_low:.1%}–{row.wilson_high:.1%}", axis=1
        )
        model_table.to_sql("model_table", connection, if_exists="replace", index=False)
        for table_name in [
            "model_summary",
            "gate_summary",
            "pairwise_comparisons",
            "lift_type_summary",
            "feature_family_summary",
            "compactness_summary",
            "model_table",
        ]:
            connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
    (REPORT_DIR / "data_quality.json").write_text(json.dumps(quality, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {
        "scope": "Frozen Python-150, four OpenHands configurations, 150 tasks each",
        "data_quality": quality,
        "headline": dataframe_records(tables["model_summary"]),
        "task_solve_count": {
            str(k): int(v)
            for k, v in tables["task_difficulty"]["models_solved"].value_counts().sort_index().items()
        },
        "caveat": quality["eligibility_caveat"],
    }
    (REPORT_DIR / "analysis_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    artifact = build_artifact(quality, tables)
    (REPORT_DIR / "artifact.json").write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_chart_map()


def run_analysis(write_notebook_file: bool = True) -> dict[str, object]:
    results, taxonomy = load_inputs()
    quality = validate_inputs(results, taxonomy)
    tables = summarize(results, taxonomy)
    write_outputs(quality, tables)
    render_figures(tables)
    if write_notebook_file:
        write_notebook(quality, tables)
    return {"quality": quality, "tables": tables}


def main() -> None:
    outputs = run_analysis(write_notebook_file=True)
    model_summary = outputs["tables"]["model_summary"]
    print("Python-150 exploratory analysis complete")
    print(model_summary[["model", "functional_pass", "assigned", "functional_rate"]].to_string(index=False))
    print(f"Figures: {FIGURE_DIR}")
    print(f"Tables: {TABLE_DIR}")


if __name__ == "__main__":
    main()
