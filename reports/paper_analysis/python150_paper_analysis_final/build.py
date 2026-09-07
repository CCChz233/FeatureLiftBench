#!/usr/bin/env python3
"""Freeze Python-150 paper-analysis package. Does not run agents.

Reads reports/paper_analysis/python150_prime_v2_analysis_20260905/task_results.csv
and writes CSV/JSON/figures plus summary_final.md.
"""
from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.formula.api as smf
from scipy import stats

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "python150_prime_v2_analysis_20260905"
ROOT = HERE.parents[2]

MODELS = [
    ("deepseek-v4-pro", "Pro"),
    ("deepseek-v4-flash", "Flash"),
    ("gpt-5.6-luna", "Luna"),
    ("glm-5.3-flash", "GLM"),
    ("qwen3.6-35b-a3b-fp8", "Qwen"),
    ("gpt-oss-120b", "OSS"),
]
MODEL_KEYS = [k for k, _ in MODELS]
SHORT = {k: s for k, s in MODELS}
STRONG3 = ["deepseek-v4-pro", "deepseek-v4-flash", "gpt-5.6-luna"]
FIVE_NO_GLM = [k for k, _ in MODELS if k != "glm-5.3-flash"]
LIFT = ["Direct", "Adapted", "Composite"]
CORE_COLOR = "#4C78A8"
HARD_COLOR = "#F58518"
PASS_COLOR = "#54A24B"
FAIL_COLOR = "#E45756"

plt.rcParams.update(
    {
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "legend.fontsize": 9,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.dpi": 140,
    }
)


def _bool(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def _opt_bool(value: Any) -> bool | None:
    text = str(value).strip().lower()
    if text in {"", "none", "nan"}:
        return None
    return text in {"true", "1", "yes"}


def _float(value: Any) -> float | None:
    text = str(value).strip()
    if text in {"", "none", "nan"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def wilson(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total <= 0:
        return (0.0, 0.0)
    rate = successes / total
    denom = 1 + z * z / total
    center = (rate + z * z / (2 * total)) / denom
    margin = z * math.sqrt(rate * (1 - rate) / total + z * z / (4 * total * total)) / denom
    return (max(0.0, center - margin), min(1.0, center + margin))


def pct(n: int, d: int) -> str:
    return "—" if d == 0 else f"{100 * n / d:.1f}%"


def rate(n: int, d: int) -> str:
    return "—" if d == 0 else f"{n}/{d} ({pct(n, d)})"


def median(values: list[float]) -> float | None:
    clean = [float(v) for v in values if v is not None]
    if not clean:
        return None
    clean.sort()
    mid = len(clean) // 2
    if len(clean) % 2:
        return clean[mid]
    return (clean[mid - 1] + clean[mid]) / 2


def quantile(values: list[float], q: float) -> float | None:
    clean = sorted(float(v) for v in values if v is not None)
    if not clean:
        return None
    idx = q * (len(clean) - 1)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return clean[lo]
    w = idx - lo
    return clean[lo] * (1 - w) + clean[hi] * w


def mean(values: list[float]) -> float | None:
    clean = [float(v) for v in values if v is not None]
    if not clean:
        return None
    return sum(clean) / len(clean)


def pass_compactness(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """RRES / copy among Functional Pass artifacts only."""
    out = []
    for key, short in MODELS:
        passed = [r for r in rows if r["model"] == key and r["functional_pass"]]
        rres = [r["rres"] for r in passed if r["rres"] is not None]
        copy = [r["copied_fraction"] for r in passed if r["copied_fraction"] is not None]
        q1_r, q3_r = quantile(rres, 0.25), quantile(rres, 0.75)
        q1_c, q3_c = quantile(copy, 0.25), quantile(copy, 0.75)
        out.append(
            {
                "model": key,
                "label": short,
                "n_pass": len(passed),
                "n_rres": len(rres),
                "n_copy": len(copy),
                "rres_mean": mean(rres),
                "rres_median": median(rres),
                "rres_q1": q1_r,
                "rres_q3": q3_r,
                "rres_iqr": None if q1_r is None or q3_r is None else q3_r - q1_r,
                "copy_mean": mean(copy),
                "copy_median": median(copy),
                "copy_q1": q1_c,
                "copy_q3": q3_c,
                "copy_iqr": None if q1_c is None or q3_c is None else q3_c - q1_c,
            }
        )
    return out


def load_task_results() -> list[dict[str, Any]]:
    rows = []
    with (SRC / "task_results.csv").open(newline="", encoding="utf-8") as handle:
        for raw in csv.DictReader(handle):
            row = dict(raw)
            row["hard3"] = _bool(raw["hard3"])
            row["functional_pass"] = _bool(raw["functional_pass"])
            row["usable_submission"] = _bool(raw["usable_submission"])
            row["artifact_fail"] = _bool(raw["artifact_fail"])
            row["build_pass"] = _opt_bool(raw["build_pass"])
            row["public_pass"] = _opt_bool(raw["public_pass"])
            row["hidden_pass"] = _opt_bool(raw["hidden_pass"])
            row["isolation_pass"] = _opt_bool(raw["isolation_pass"])
            row["copied_fraction"] = _float(raw["copied_fraction"])
            row["rres"] = _float(raw["rres"])
            row["process_total_tokens"] = _float(raw.get("process_total_tokens"))
            row["process_incremental_tokens"] = _float(raw.get("process_incremental_tokens"))
            row["process_completion_tokens"] = _float(raw.get("process_completion_tokens"))
            row["process_api_calls"] = _float(raw.get("process_api_calls"))
            row["process_assistant_steps"] = _float(raw.get("process_assistant_steps"))
            row["process_duration_seconds"] = _float(raw.get("process_duration_seconds"))
            row["process_usage_unverified"] = _bool(raw.get("process_usage_unverified"))
            rows.append(row)
    return rows


def load_f3() -> dict[tuple[str, str], dict[str, str]]:
    path = SRC / "failure_root_cause_annotations.csv"
    out: dict[tuple[str, str], dict[str, str]] = {}
    if not path.is_file():
        return out
    with path.open(newline="", encoding="utf-8") as handle:
        for raw in csv.DictReader(handle):
            out[(raw["task_id"], raw["model"])] = raw
    return out


def by_model(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["model"]].append(row)
    return grouped


def save_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            flat = {}
            for key, value in row.items():
                if isinstance(value, (list, dict)):
                    flat[key] = json.dumps(value, ensure_ascii=False)
                elif isinstance(value, float):
                    flat[key] = f"{value:.6g}"
                elif value is None:
                    flat[key] = ""
                else:
                    flat[key] = value
            writer.writerow(flat)


def save_fig(fig: plt.Figure, stem: str) -> None:
    out = HERE / "fig"
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(out / f"{stem}.png", bbox_inches="tight")
    plt.close(fig)


def difficulty_band(n_solved: int, n_models: int) -> str:
    if n_solved == 0:
        return "unsolved"
    if n_solved <= 2:
        return "hard_tail"
    if n_solved <= n_models - 2:
        return "mixed"
    if n_solved < n_models:
        return "easy"
    return "solved_by_all"


def task_difficulty_table(rows: list[dict[str, Any]], keys: list[str]) -> list[dict[str, Any]]:
    by_task: dict[str, dict[str, Any]] = {}
    for row in rows:
        if row["model"] not in keys:
            continue
        item = by_task.setdefault(
            row["task_id"],
            {
                "task_id": row["task_id"],
                "construction": "hard3" if row["hard3"] else "core100",
                "hard3": row["hard3"],
                "lift_type": row["lift_type"],
                "feature_family": row["feature_family"],
            },
        )
        item[f"pass_{SHORT[row['model']]}"] = int(row["functional_pass"])
        item[f"stage_{SHORT[row['model']]}"] = row["first_failure_stage"]
    n_models = len(keys)
    out = []
    for task_id, item in sorted(by_task.items()):
        solved = sum(int(item.get(f"pass_{SHORT[k]}", 0)) for k in keys)
        item["num_models_solved"] = solved
        item["n_models"] = n_models
        item["solved_over_n"] = f"{solved}/{n_models}"
        item["difficulty_level"] = difficulty_band(solved, n_models)
        out.append(item)
    return out


def spectrum_counts(table: list[dict[str, Any]], n_models: int) -> dict[str, Any]:
    counts = {k: {"core100": 0, "hard3": 0} for k in range(n_models + 1)}
    for row in table:
        k = int(row["num_models_solved"])
        split = "hard3" if row["hard3"] else "core100"
        counts[k][split] += 1
    return {
        "n_models": n_models,
        "bins": [
            {
                "solved": k,
                "label": f"{k}/{n_models}",
                "core100": counts[k]["core100"],
                "hard3": counts[k]["hard3"],
                "total": counts[k]["core100"] + counts[k]["hard3"],
            }
            for k in range(n_models + 1)
        ],
        "unsolved_total": counts[0]["core100"] + counts[0]["hard3"],
        "unsolved_hard3": counts[0]["hard3"],
        "all_solved": counts[n_models]["core100"] + counts[n_models]["hard3"],
    }


def plot_spectrum(spec: dict[str, Any], stem: str, title: str) -> None:
    bins = spec["bins"]
    x = np.arange(len(bins))
    core = [b["core100"] for b in bins]
    hard = [b["hard3"] for b in bins]
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.bar(x, core, color=CORE_COLOR, label="Core-100")
    ax.bar(x, hard, bottom=core, color=HARD_COLOR, label="hard3")
    ax.set_xticks(x, [b["label"] for b in bins])
    ax.set_xlabel("Models solving the task")
    ax.set_ylabel("Tasks")
    ax.set_title(title)
    ax.legend(frameon=False)
    ymax = max(b["total"] for b in bins)
    ax.set_ylim(0, ymax * 1.12 if ymax else 1)
    for i, b in enumerate(bins):
        if b["total"]:
            ax.text(i, b["total"] + ymax * 0.02, str(b["total"]), ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    save_fig(fig, stem)


def lift_inventory(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    for row in rows:
        if row["model"] != MODEL_KEYS[0]:
            continue
        seen[row["task_id"]] = row
    out = []
    for split_name, pred in (("core100", lambda r: not r["hard3"]), ("hard3", lambda r: r["hard3"])):
        rec = {"split": split_name, "n_tasks": 0}
        for lift in LIFT:
            n = sum(1 for r in seen.values() if pred(r) and r["lift_type"] == lift)
            rec[lift] = n
            rec["n_tasks"] += n
        out.append(rec)
    return out


def construction_chi2(rows: list[dict[str, Any]], model_key: str) -> dict[str, Any]:
    items = [r for r in rows if r["model"] == model_key]
    core_p = sum(1 for r in items if (not r["hard3"]) and r["functional_pass"])
    core_f = sum(1 for r in items if (not r["hard3"]) and (not r["functional_pass"]))
    hard_p = sum(1 for r in items if r["hard3"] and r["functional_pass"])
    hard_f = sum(1 for r in items if r["hard3"] and (not r["functional_pass"]))
    chi2, p, _, _ = stats.chi2_contingency([[core_p, core_f], [hard_p, hard_f]])
    return {
        "model": SHORT[model_key],
        "core_pass": core_p,
        "core_n": core_p + core_f,
        "hard3_pass": hard_p,
        "hard3_n": hard_p + hard_f,
        "chi2": float(chi2),
        "p": float(p),
    }


def lift_hard3_cells(rows: list[dict[str, Any]], model_key: str | None) -> list[dict[str, Any]]:
    subset = rows if model_key is None else [r for r in rows if r["model"] == model_key]
    out = []
    for split_name, pred in (("core100", lambda r: not r["hard3"]), ("hard3", lambda r: r["hard3"])):
        rec: dict[str, Any] = {
            "model": "pooled" if model_key is None else model_key,
            "label": "pooled" if model_key is None else SHORT[model_key],
            "split": split_name,
        }
        for lift in LIFT:
            items = [r for r in subset if pred(r) and r["lift_type"] == lift]
            p = sum(1 for r in items if r["functional_pass"])
            rec[lift] = rate(p, len(items))
            rec[f"{lift}_passed"] = p
            rec[f"{lift}_n"] = len(items)
            rec[f"{lift}_empty"] = sum(1 for r in items if not r["usable_submission"])
        out.append(rec)
    return out


def fit_logit(rows: list[dict[str, Any]], keys: list[str], tag: str) -> dict[str, Any]:
    subset = [r for r in rows if r["model"] in keys]
    import pandas as pd

    frame = pd.DataFrame(
        {
            "passed": [int(r["functional_pass"]) for r in subset],
            "hard3": [int(r["hard3"]) for r in subset],
            "lift_type": [r["lift_type"] for r in subset],
            "model": [SHORT[r["model"]] for r in subset],
            "task_id": [r["task_id"] for r in subset],
            "usable": [int(r["usable_submission"]) for r in subset],
        }
    )
    formula = 'passed ~ C(model) + hard3 + C(lift_type, Treatment("Direct"))'
    model = smf.logit(formula, data=frame)
    fit = model.fit(disp=False, cov_type="cluster", cov_kwds={"groups": frame["task_id"]})
    params = []
    for name in fit.params.index:
        params.append(
            {
                "term": name,
                "coef": float(fit.params[name]),
                "std_err": float(fit.bse[name]),
                "z": float(fit.tvalues[name]),
                "p": float(fit.pvalues[name]),
                "or": float(math.exp(fit.params[name])),
            }
        )
    return {
        "tag": tag,
        "n": int(len(frame)),
        "n_tasks": int(frame["task_id"].nunique()),
        "formula": formula,
        "cluster": "task_id",
        "pseudo_r2": float(fit.prsquared),
        "llf": float(fit.llf),
        "params": params,
        "composite_p": next(
            (p["p"] for p in params if "Composite" in p["term"]),
            None,
        ),
        "adapted_p": next((p["p"] for p in params if "Adapted" in p["term"]), None),
        "hard3_p": next((p["p"] for p in params if p["term"] == "hard3"), None),
        "composite_or": next((p["or"] for p in params if "Composite" in p["term"]), None),
        "adapted_or": next((p["or"] for p in params if "Adapted" in p["term"]), None),
        "hard3_or": next((p["or"] for p in params if p["term"] == "hard3"), None),
        "summary_text": str(fit.summary()),
    }


def rank_biserial(x: np.ndarray, y: np.ndarray) -> float | None:
    delta = np.asarray(x, dtype=float) - np.asarray(y, dtype=float)
    delta = delta[delta != 0]
    if len(delta) == 0:
        return None
    ranks = stats.rankdata(np.abs(delta))
    r_plus = float(ranks[delta > 0].sum())
    r_minus = float(ranks[delta < 0].sum())
    n = len(delta)
    return (r_plus - r_minus) / (n * (n + 1) / 2)


def paired_compactness(rows: list[dict[str, Any]], a: str, b: str) -> dict[str, Any]:
    by_a = {r["task_id"]: r for r in rows if r["model"] == a and r["functional_pass"]}
    by_b = {r["task_id"]: r for r in rows if r["model"] == b and r["functional_pass"]}
    common = sorted(set(by_a) & set(by_b))
    xa, xb, rresa, rresb = [], [], [], []
    pairs = []
    for tid in common:
        ca = by_a[tid]["copied_fraction"]
        cb = by_b[tid]["copied_fraction"]
        if ca is None or cb is None:
            continue
        xa.append(ca)
        xb.append(cb)
        rresa.append(by_a[tid]["rres"])
        rresb.append(by_b[tid]["rres"])
        pairs.append(
            {
                "task_id": tid,
                f"copy_{SHORT[a]}": ca,
                f"copy_{SHORT[b]}": cb,
                "diff": ca - cb,
                "hard3": by_a[tid]["hard3"],
                "lift_type": by_a[tid]["lift_type"],
            }
        )
    xa_n = np.array(xa)
    xb_n = np.array(xb)
    diff = xa_n - xb_n
    w = stats.wilcoxon(xa_n, xb_n, zero_method="wilcox", alternative="two-sided")
    return {
        "a": a,
        "b": b,
        "label_a": SHORT[a],
        "label_b": SHORT[b],
        "n": int(len(xa)),
        "median_a": float(np.median(xa_n)),
        "median_b": float(np.median(xb_n)),
        "median_diff": float(np.median(diff)),
        "mean_diff": float(np.mean(diff)),
        "n_a_greater": int(np.sum(diff > 0)),
        "n_b_greater": int(np.sum(diff < 0)),
        "n_tie": int(np.sum(diff == 0)),
        "wilcoxon_stat": float(w.statistic),
        "wilcoxon_p": float(w.pvalue),
        "rank_biserial": rank_biserial(xa_n, xb_n),
        "rres_median_a": median([v for v in rresa if v is not None]),
        "rres_median_b": median([v for v in rresb if v is not None]),
        "pairs": pairs,
    }


def plot_paired_copy(pro_luna: dict[str, Any], flash_luna: dict[str, Any]) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.5))
    pairs = pro_luna["pairs"]
    x = [p["copy_Pro"] for p in pairs]
    y = [p["copy_Luna"] for p in pairs]
    from matplotlib.lines import Line2D

    colors = [HARD_COLOR if p["hard3"] else CORE_COLOR for p in pairs]
    axes[0].scatter(x, y, s=18, alpha=0.75, c=colors, edgecolors="none")
    axes[0].plot([0, 1], [0, 1], color="#888", lw=1, ls="--")
    axes[0].set_xlim(0, 1)
    axes[0].set_ylim(0, 1)
    axes[0].set_xlabel("Pro copy fraction")
    axes[0].set_ylabel("Luna copy fraction")
    axes[0].set_title(f"Paired scatter (n={pro_luna['n']})")
    axes[0].set_aspect("equal", adjustable="box")
    axes[0].legend(
        handles=[
            Line2D([0], [0], marker="o", color="none", markerfacecolor=CORE_COLOR, markersize=6, label="Core-100"),
            Line2D([0], [0], marker="o", color="none", markerfacecolor=HARD_COLOR, markersize=6, label="hard3"),
        ],
        frameon=False,
        loc="upper left",
    )

    xs = np.sort(x)
    ys = np.sort(y)
    axes[1].plot(xs, np.linspace(0, 1, len(xs)), color=CORE_COLOR, label="Pro")
    axes[1].plot(ys, np.linspace(0, 1, len(ys)), color=HARD_COLOR, label="Luna")
    axes[1].set_xlim(0, 1)
    axes[1].set_ylim(0, 1)
    axes[1].set_xlabel("Copy fraction")
    axes[1].set_ylabel("ECDF")
    axes[1].set_title("Paired ECDF")
    axes[1].legend(frameon=False)

    data = [x, y]
    bp = axes[2].boxplot(data, tick_labels=["Pro", "Luna"], patch_artist=True, widths=0.55)
    for patch, color in zip(bp["boxes"], [CORE_COLOR, HARD_COLOR]):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    axes[2].set_ylim(0, 1)
    axes[2].set_ylabel("Copy fraction")
    axes[2].set_title("Paired distribution")
    fig.suptitle("Same-task compactness: Pro vs Luna", y=1.02, fontsize=11)
    fig.tight_layout()
    save_fig(fig, "fig_paired_copy")

    fig2, ax = plt.subplots(figsize=(4.2, 4.0))
    fp = flash_luna["pairs"]
    ax.scatter(
        [p["copy_Flash"] for p in fp],
        [p["copy_Luna"] for p in fp],
        s=18,
        alpha=0.75,
        c=CORE_COLOR,
        edgecolors="none",
    )
    ax.plot([0, 1], [0, 1], color="#888", lw=1, ls="--")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Flash copy fraction")
    ax.set_ylabel("Luna copy fraction")
    ax.set_title(f"Flash vs Luna (n={flash_luna['n']})")
    ax.set_aspect("equal", adjustable="box")
    fig2.tight_layout()
    save_fig(fig2, "fig_paired_copy_flash_luna")


def independent_gates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for key, short in MODELS:
        items = [r for r in rows if r["model"] == key]
        usable = [r for r in items if r["usable_submission"]]
        rec = {
            "model": key,
            "label": short,
            "n": len(items),
            "usable": len(usable),
            "empty": len(items) - len(usable),
            "functional_pass": sum(1 for r in items if r["functional_pass"]),
            "build_fail": sum(1 for r in usable if r["build_pass"] is False),
            "public_fail": sum(1 for r in usable if r["public_pass"] is False),
            "hidden_fail": sum(1 for r in usable if r["hidden_pass"] is False),
            "isolation_fail": sum(1 for r in usable if r["isolation_pass"] is False),
            "isolation_fail_given_build": sum(
                1 for r in usable if r["build_pass"] is True and r["isolation_pass"] is False
            ),
            "isolation_fail_given_behavior": sum(
                1
                for r in usable
                if r["build_pass"] is True
                and r["public_pass"] is True
                and r["hidden_pass"] is True
                and r["isolation_pass"] is False
            ),
            "first_isolation": sum(1 for r in items if r["first_failure_stage"] == "isolation_failure"),
        }
        out.append(rec)
    return out


def plot_independent_gates(table: list[dict[str, Any]]) -> None:
    labels = [r["label"] for r in table]
    x = np.arange(len(labels))
    width = 0.2
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    series = [
        ("Build fail", [r["build_fail"] for r in table], "#9D755D"),
        ("Public fail", [r["public_fail"] for r in table], HARD_COLOR),
        ("Hidden fail", [r["hidden_fail"] for r in table], CORE_COLOR),
        ("Isolation fail", [r["isolation_fail"] for r in table], "#B279A2"),
    ]
    for i, (name, vals, color) in enumerate(series):
        ax.bar(x + (i - 1.5) * width, vals, width, label=name, color=color)
    ax.set_xticks(x, labels)
    ax.set_ylabel("Tasks (non-exclusive)")
    ax.set_title("Independent gate failures among delivered packages")
    ax.legend(frameon=False, ncol=2)
    fig.tight_layout()
    save_fig(fig, "fig_independent_gates")


def plot_funnel(rows: list[dict[str, Any]]) -> None:
    stages = [
        ("missing_submission", "Missing"),
        ("build_failure", "Build"),
        ("public_failure", "Public"),
        ("hidden_failure", "Hidden"),
        ("isolation_failure", "Isolation"),
        ("functional_pass", "Pass"),
    ]
    colors = ["#7F7F7F", "#9D755D", HARD_COLOR, CORE_COLOR, "#B279A2", PASS_COLOR]
    labels = [s for _, s in MODELS]
    fig, ax = plt.subplots(figsize=(7.4, 3.8))
    bottoms = np.zeros(len(MODELS))
    x = np.arange(len(MODELS))
    grouped = by_model(rows)
    for (stage, name), color in zip(stages, colors):
        vals = []
        for key, _ in MODELS:
            vals.append(sum(1 for r in grouped[key] if r["first_failure_stage"] == stage))
        ax.bar(x, vals, bottom=bottoms, color=color, label=name)
        bottoms += np.array(vals, dtype=float)
    ax.set_xticks(x, labels)
    ax.set_ylabel("Tasks")
    ax.set_title("First-failure funnel (mutually exclusive)")
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.18))
    ax.set_ylim(0, 160)
    fig.tight_layout()
    save_fig(fig, "fig_failure_stage_funnel")


def plot_lift_hard3(cells: list[dict[str, Any]]) -> None:
    # Pro/Flash/Luna rates as grouped bars within Core vs hard3
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.5), sharey=True)
    for ax, split in zip(axes, ("core100", "hard3")):
        x = np.arange(len(LIFT))
        width = 0.25
        for i, key in enumerate(STRONG3):
            rec = next(c for c in cells if c["model"] == key and c["split"] == split)
            vals = [100 * rec[f"{lift}_passed"] / rec[f"{lift}_n"] if rec[f"{lift}_n"] else 0 for lift in LIFT]
            ax.bar(x + (i - 1) * width, vals, width, label=SHORT[key])
        n_direct = 53 if split == "core100" else 3
        n_adapted = 44 if split == "core100" else 32
        n_composite = 3 if split == "core100" else 15
        ax.set_xticks(x, [f"Direct\n(n={n_direct})", f"Adapted\n(n={n_adapted})", f"Composite\n(n={n_composite})"])
        ax.set_title("Core-100" if split == "core100" else "hard3")
        ax.set_ylabel("Functional Pass (%)" if split == "core100" else "")
        ax.set_ylim(0, 105)
    axes[0].legend(frameon=False)
    fig.suptitle("Lift type within construction split (Pro / Flash / Luna)", y=1.02)
    fig.tight_layout()
    save_fig(fig, "fig_lift_type_hard3")


def token_tables(rows: list[dict[str, Any]]) -> dict[str, Any]:
    models = []
    core_hard = []
    pass_fail = []
    for key, short in MODELS:
        items = [r for r in rows if r["model"] == key]
        tok_field = "process_incremental_tokens" if key.startswith("deepseek") else "process_total_tokens"
        token_vals = [r[tok_field] for r in items if r[tok_field]]
        step_vals = [r["process_assistant_steps"] for r in items if r["process_assistant_steps"] is not None]
        models.append(
            {
                "model": key,
                "label": short,
                "pass": sum(1 for r in items if r["functional_pass"]),
                "token_field": tok_field,
                "n_tokens": len(token_vals),
                "median_tokens": median(token_vals),
                "p90_tokens": quantile(token_vals, 0.9),
                "median_steps": median(step_vals),
                "p90_steps": quantile(step_vals, 0.9),
                "usage_unverified": sum(1 for r in items if r["process_usage_unverified"]),
            }
        )
        for flag, name in ((False, "core100"), (True, "hard3")):
            sub = [r for r in items if r["hard3"] is flag]
            tv = [r[tok_field] for r in sub if r[tok_field]]
            sv = [r["process_assistant_steps"] for r in sub if r["process_assistant_steps"] is not None]
            pv = sum(1 for r in sub if r["functional_pass"])
            core_hard.append(
                {
                    "model": short,
                    "split": name,
                    "n": len(sub),
                    "passed": pv,
                    "median_tokens": median(tv),
                    "n_tokens": len(tv),
                    "median_steps": median(sv),
                }
            )
        for flag, name in ((True, "pass"), (False, "fail")):
            sub = [r for r in items if r["functional_pass"] is flag]
            tv = [r[tok_field] for r in sub if r[tok_field]]
            sv = [r["process_assistant_steps"] for r in sub if r["process_assistant_steps"] is not None]
            pass_fail.append(
                {
                    "model": short,
                    "outcome": name,
                    "n": len(sub),
                    "median_tokens": median(tv),
                    "n_tokens": len(tv),
                    "median_steps": median(sv),
                }
            )
    tests = []
    for key, short in MODELS:
        items = [r for r in rows if r["model"] == key]
        tok_field = "process_incremental_tokens" if key.startswith("deepseek") else "process_total_tokens"
        core = [r[tok_field] for r in items if (not r["hard3"]) and r[tok_field]]
        hard = [r[tok_field] for r in items if r["hard3"] and r[tok_field]]
        passed = [r[tok_field] for r in items if r["functional_pass"] and r[tok_field]]
        failed = [r[tok_field] for r in items if (not r["functional_pass"]) and r[tok_field]]
        rec: dict[str, Any] = {"model": short, "token_field": tok_field}
        if len(core) >= 5 and len(hard) >= 5:
            u = stats.mannwhitneyu(hard, core, alternative="two-sided")
            rec["core_vs_hard3_p"] = float(u.pvalue)
            rec["core_vs_hard3_median"] = [median(core), median(hard)]
        if len(passed) >= 5 and len(failed) >= 5:
            u = stats.mannwhitneyu(failed, passed, alternative="two-sided")
            rec["pass_vs_fail_p"] = float(u.pvalue)
            rec["pass_vs_fail_median"] = [median(passed), median(failed)]
        tests.append(rec)
    return {"by_model": models, "core_hard3": core_hard, "pass_fail": pass_fail, "tests": tests}


def _token_grouped_bars(ax, models: list[str], left: list[float], right: list[float], left_name: str, right_name: str, c1: str, c2: str, ylabel: str, title: str) -> None:
    x = np.arange(len(models))
    width = 0.35
    ax.bar(x - width / 2, [v / 1000 for v in left], width, color=c1, label=left_name)
    ax.bar(x + width / 2, [v / 1000 for v in right], width, color=c2, label=right_name)
    ax.set_xticks(x, models)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(frameon=False)


def plot_token_efficiency(tok: dict[str, Any]) -> None:
    # Same-accounting comparison: Pro/Flash incremental only. Qwen/OSS totals are a different ledger.
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.4))
    models = ["Pro", "Flash"]
    ch = tok["core_hard3"]
    pf = tok["pass_fail"]
    core = [next(r["median_tokens"] for r in ch if r["model"] == m and r["split"] == "core100") for m in models]
    hard = [next(r["median_tokens"] for r in ch if r["model"] == m and r["split"] == "hard3") for m in models]
    pvals = [next(r["median_tokens"] for r in pf if r["model"] == m and r["outcome"] == "pass") for m in models]
    fvals = [next(r["median_tokens"] for r in pf if r["model"] == m and r["outcome"] == "fail") for m in models]
    _token_grouped_bars(axes[0], models, core, hard, "Core-100", "hard3", CORE_COLOR, HARD_COLOR, "Median incremental tokens (thousands)", "Core vs hard3")
    _token_grouped_bars(axes[1], models, pvals, fvals, "Pass", "Fail", PASS_COLOR, FAIL_COLOR, "", "Pass vs fail")
    fig.suptitle("Token diagnostics (incremental = uncached prompt + completion)", y=1.02, fontsize=10)
    fig.tight_layout()
    save_fig(fig, "fig_token_efficiency")


def discordant_pro_flash(rows: list[dict[str, Any]], f3: dict[tuple[str, str], dict[str, str]]) -> dict[str, Any]:
    pro = {r["task_id"]: r for r in rows if r["model"] == "deepseek-v4-pro"}
    flash = {r["task_id"]: r for r in rows if r["model"] == "deepseek-v4-flash"}
    pro_wins, flash_wins = [], []
    for tid in sorted(pro):
        a, b = pro[tid], flash[tid]
        if a["functional_pass"] and not b["functional_pass"]:
            rec = _discord_row(tid, a, b, "pro_wins", f3)
            pro_wins.append(rec)
        elif b["functional_pass"] and not a["functional_pass"]:
            rec = _discord_row(tid, a, b, "flash_wins", f3)
            flash_wins.append(rec)
    def tally(items: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "n": len(items),
            "hard3": sum(1 for r in items if r["hard3"]),
            "lift": dict(Counter(r["lift_type"] for r in items)),
            "flash_stage": dict(Counter(r["flash_stage"] for r in items)),
            "pro_stage": dict(Counter(r["pro_stage"] for r in items)),
            "flash_cause": dict(Counter(r["flash_cause"] for r in items)),
            "pro_cause": dict(Counter(r["pro_cause"] for r in items)),
        }
    return {
        "pro_wins": pro_wins,
        "flash_wins": flash_wins,
        "pro_wins_tally": tally(pro_wins),
        "flash_wins_tally": tally(flash_wins),
    }


def _discord_row(
    tid: str,
    pro: dict[str, Any],
    flash: dict[str, Any],
    pair: str,
    f3: dict[tuple[str, str], dict[str, str]],
) -> dict[str, Any]:
    pro_ann = f3.get((tid, "deepseek-v4-pro"), {})
    flash_ann = f3.get((tid, "deepseek-v4-flash"), {})
    return {
        "task_id": tid,
        "pair": pair,
        "hard3": pro["hard3"],
        "lift_type": pro["lift_type"],
        "pro_stage": pro["first_failure_stage"],
        "flash_stage": flash["first_failure_stage"],
        "pro_cause": pro_ann.get("root_cause_primary") or "",
        "flash_cause": flash_ann.get("root_cause_primary") or "",
        "pro_eligibility": pro_ann.get("evidence_eligibility") or "",
        "flash_eligibility": flash_ann.get("evidence_eligibility") or "",
    }


def fmt_num(value: float | None, digits: int = 0) -> str:
    if value is None:
        return "—"
    if digits == 0:
        return f"{value:.0f}"
    return f"{value:.{digits}f}"


def fmt_p(p: float | None) -> str:
    if p is None:
        return "—"
    if p < 1e-4:
        return f"{p:.1e}"
    return f"{p:.3g}"


def write_summary(stats_blob: dict[str, Any]) -> None:
    spec6 = stats_blob["spectrum6"]
    spec5 = stats_blob["spectrum5"]
    logit6 = stats_blob["logit_all6"]
    logit3 = stats_blob["logit_strong3"]
    pl = stats_blob["paired_pro_luna"]
    fl = stats_blob["paired_flash_luna"]
    gates = {r["label"]: r for r in stats_blob["independent_gates"]}
    disc = stats_blob["pro_flash_discordant"]
    tok = stats_blob["token"]
    lb = stats_blob["leaderboard"]

    def lb_row(short: str) -> dict[str, Any]:
        return next(r for r in lb if r["short"] == short)

    def fmt_count(d: dict[str, Any]) -> str:
        return ", ".join(f"{k} {v}" for k, v in d.items()) if d else "—"

    tok_lines = "\n".join(
        "| {label} | {passed} | {med} | {p90} | {steps} | {n} |".format(
            label=r["label"],
            passed=r["pass"],
            med=fmt_num(r["median_tokens"]),
            p90=fmt_num(r["p90_tokens"]),
            steps=fmt_num(r["median_steps"]),
            n=r["n_tokens"],
        )
        for r in tok["by_model"]
    )
    spec_lines = "\n".join(
        f"| {b['label']} | {b['core100']} | {b['hard3']} | {b['total']} |" for b in spec6["bins"]
    )
    spec5_lines = "\n".join(
        f"| {b['label']} | {b['core100']} | {b['hard3']} | {b['total']} |" for b in spec5["bins"]
    )
    pro_core_h, pro_hard_h = next(
        t["core_vs_hard3_median"] for t in tok["tests"] if t["model"] == "Pro" and "core_vs_hard3_median" in t
    )
    pro_core_p = next(t.get("core_vs_hard3_p") for t in tok["tests"] if t["model"] == "Pro")
    inv = stats_blob["lift_inventory"]
    inv_core = next(r for r in inv if r["split"] == "core100")
    inv_hard = next(r for r in inv if r["split"] == "hard3")
    chi_pro = next(r for r in stats_blob["construction_chi2"] if r["model"] == "Pro")
    chi_flash = next(r for r in stats_blob["construction_chi2"] if r["model"] == "Flash")
    pooled6_core = next(c for c in stats_blob["lift_hard3"] if c["label"] == "pooled" and c["split"] == "core100")
    pooled6_hard = next(c for c in stats_blob["lift_hard3"] if c["label"] == "pooled" and c["split"] == "hard3")
    pooled5_core = next(c for c in stats_blob["lift_hard3"] if c["label"] == "pooled_five" and c["split"] == "core100")
    pooled5_hard = next(c for c in stats_blob["lift_hard3"] if c["label"] == "pooled_five" and c["split"] == "hard3")
    iso_residual = sum(g["isolation_fail_given_behavior"] for g in stats_blob["independent_gates"])
    iso_raw = sum(g["isolation_fail"] for g in stats_blob["independent_gates"])
    unsolved6 = next(b for b in spec6["bins"] if b["solved"] == 0)
    all6 = next(b for b in spec6["bins"] if b["solved"] == 6)

    text = f"""# Python-150 freeze v2 — paper analysis final

Input: `python150_prime_v2_analysis_20260905/task_results.csv`.
Functional Pass = build ∧ public ∧ hidden ∧ isolation. Empty submissions fail.
Do not use `run.status`. Finding 3 remains an assistant L1 census on Pro+Flash
artifact failures (n=63), not gold. Official Hard-50 is appendix-only.

Reproduce: `.venv/bin/python reports/paper_analysis/python150_paper_analysis_final/build.py`

Headline models (6): Pro, Flash, Luna, GLM-5.3-Flash, Qwen, OSS.
Spectrum figures report both 6-model (official) and 5-model (no GLM) counts.

---

## RQ1 Overall capability

**Numbers.**

| Model | Pass | Wilson 95% | Core-100 | hard3 | Empty |
| --- | ---: | ---: | ---: | ---: | ---: |
| Pro | {lb_row('Pro')['display']} | {lb_row('Pro')['wilson']} | {lb_row('Pro')['core']} | {lb_row('Pro')['hard3']} | {lb_row('Pro')['empty']} |
| Flash | {lb_row('Flash')['display']} | {lb_row('Flash')['wilson']} | {lb_row('Flash')['core']} | {lb_row('Flash')['hard3']} | {lb_row('Flash')['empty']} |
| Luna | {lb_row('Luna')['display']} | {lb_row('Luna')['wilson']} | {lb_row('Luna')['core']} | {lb_row('Luna')['hard3']} | {lb_row('Luna')['empty']} |
| GLM | {lb_row('GLM')['display']} | {lb_row('GLM')['wilson']} | {lb_row('GLM')['core']} | {lb_row('GLM')['hard3']} | {lb_row('GLM')['empty']} |
| Qwen | {lb_row('Qwen')['display']} | {lb_row('Qwen')['wilson']} | {lb_row('Qwen')['core']} | {lb_row('Qwen')['hard3']} | {lb_row('Qwen')['empty']} |
| OSS | {lb_row('OSS')['display']} | {lb_row('OSS')['wilson']} | {lb_row('OSS')['core']} | {lb_row('OSS')['hard3']} | {lb_row('OSS')['empty']} |

McNemar Pro vs Flash: 10 / 3, p={fmt_p(stats_blob['mcnemar_pro_flash']['p'])}.
Pro vs Luna p={fmt_p(stats_blob['mcnemar_pro_luna']['p'])}. GLM vs Qwen {stats_blob['mcnemar_glm_qwen']['n10']}/{stats_blob['mcnemar_glm_qwen']['n01']}, p={fmt_p(stats_blob['mcnemar_glm_qwen']['p'])}.

**Finding 1.** Current coding agents exhibit substantial but incomplete feature-lifting capability on frozen Python-150, with large performance differences across model backends.

**Can write.** Range 24.0%–76.7%; ceiling (Pro still fails 35/150); {unsolved6['total']} tasks unsolved by all six models ({unsolved6['hard3']} of them hard3); GLM sits with Qwen, not with Luna.

**Cannot write.** Pro significantly stronger than Flash. GLM stronger than Qwen. Qwen 63/125 or GLM 68/112.

Figure: `fig/fig_failure_stage_funnel.pdf` (first-failure, exclusive). Table 1 stays as above — no extra columns.

---

## RQ2 Difficulty

### Spectrum (official 6-model)

| Solved | Core-100 | hard3 | Total |
| ---: | ---: | ---: | ---: |
{spec_lines}

Unsolved by every backend: **{unsolved6['total']}/150** ({unsolved6['hard3']} hard3, {unsolved6['core100']} Core-100).
Solved by all six: **{all6['total']}/150**.

5-model (no GLM) unsolved remains {spec5['unsolved_total']}; all-five solved {spec5['all_solved']}. Adding GLM did not unlock the unsolved set.

| Solved | Core-100 | hard3 | Total |
| ---: | ---: | ---: | ---: |
{spec5_lines}

Figure: `fig/fig_task_difficulty_spectrum.pdf`. Companion 5-model figure: `fig/fig_task_difficulty_spectrum_5model.pdf` (unsolved set unchanged).

### Lift type × hard3

Task inventory (the confounder):

| Split | Direct | Adapted | Composite | Total |
| --- | ---: | ---: | ---: | ---: |
| Core-100 | {inv_core['Direct']} | {inv_core['Adapted']} | {inv_core['Composite']} | {inv_core['n_tasks']} |
| hard3 | {inv_hard['Direct']} | {inv_hard['Adapted']} | {inv_hard['Composite']} | {inv_hard['n_tasks']} |

Direct is almost entirely Core ({inv_core['Direct']}/{inv_core['Direct']+inv_hard['Direct']}). Composite is almost entirely hard3 ({inv_hard['Composite']}/{inv_core['Composite']+inv_hard['Composite']}). Core Composite n=3 and hard3 Direct n=3 are too small for a within-split lift-type test.

Pass rates (Pro / Flash / Luna):

| Split | Direct | Adapted | Composite |
| --- | ---: | ---: | ---: |
| Core Pro | {next(c for c in stats_blob['lift_hard3'] if c['model']=='deepseek-v4-pro' and c['split']=='core100')['Direct']} | {next(c for c in stats_blob['lift_hard3'] if c['model']=='deepseek-v4-pro' and c['split']=='core100')['Adapted']} | {next(c for c in stats_blob['lift_hard3'] if c['model']=='deepseek-v4-pro' and c['split']=='core100')['Composite']} |
| hard3 Pro | {next(c for c in stats_blob['lift_hard3'] if c['model']=='deepseek-v4-pro' and c['split']=='hard3')['Direct']} | {next(c for c in stats_blob['lift_hard3'] if c['model']=='deepseek-v4-pro' and c['split']=='hard3')['Adapted']} | {next(c for c in stats_blob['lift_hard3'] if c['model']=='deepseek-v4-pro' and c['split']=='hard3')['Composite']} |
| Core Flash | {next(c for c in stats_blob['lift_hard3'] if c['model']=='deepseek-v4-flash' and c['split']=='core100')['Direct']} | {next(c for c in stats_blob['lift_hard3'] if c['model']=='deepseek-v4-flash' and c['split']=='core100')['Adapted']} | {next(c for c in stats_blob['lift_hard3'] if c['model']=='deepseek-v4-flash' and c['split']=='core100')['Composite']} |
| hard3 Flash | {next(c for c in stats_blob['lift_hard3'] if c['model']=='deepseek-v4-flash' and c['split']=='hard3')['Direct']} | {next(c for c in stats_blob['lift_hard3'] if c['model']=='deepseek-v4-flash' and c['split']=='hard3')['Adapted']} | {next(c for c in stats_blob['lift_hard3'] if c['model']=='deepseek-v4-flash' and c['split']=='hard3')['Composite']} |
| Core Luna | {next(c for c in stats_blob['lift_hard3'] if c['model']=='gpt-5.6-luna' and c['split']=='core100')['Direct']} | {next(c for c in stats_blob['lift_hard3'] if c['model']=='gpt-5.6-luna' and c['split']=='core100')['Adapted']} | {next(c for c in stats_blob['lift_hard3'] if c['model']=='gpt-5.6-luna' and c['split']=='core100')['Composite']} |
| hard3 Luna | {next(c for c in stats_blob['lift_hard3'] if c['model']=='gpt-5.6-luna' and c['split']=='hard3')['Direct']} | {next(c for c in stats_blob['lift_hard3'] if c['model']=='gpt-5.6-luna' and c['split']=='hard3')['Adapted']} | {next(c for c in stats_blob['lift_hard3'] if c['model']=='gpt-5.6-luna' and c['split']=='hard3')['Composite']} |
| Core pooled-6 | {pooled6_core['Direct']} | {pooled6_core['Adapted']} | {pooled6_core['Composite']} |
| hard3 pooled-6 | {pooled6_hard['Direct']} | {pooled6_hard['Adapted']} | {pooled6_hard['Composite']} |
| Core pooled-5 | {pooled5_core['Direct']} | {pooled5_core['Adapted']} | {pooled5_core['Composite']} |
| hard3 pooled-5 | {pooled5_hard['Direct']} | {pooled5_hard['Adapted']} | {pooled5_hard['Composite']} |

On Core, Direct ≳ Adapted > Composite, but Composite has only 3 tasks. On hard3 the order does **not** hold (Pro Composite 7/15 vs Adapted 14/32 vs Direct 0/3).

Logistic, cluster-robust SE by task: `passed ~ C(model) + hard3 + C(lift_type, Treatment(Direct))`.

| Fit | n | hard3 OR (p) | Adapted OR (p) | Composite OR (p) |
| --- | ---: | --- | --- | --- |
| Six models | {logit6['n']} | {logit6['hard3_or']:.2f} ({fmt_p(logit6['hard3_p'])}) | {logit6['adapted_or']:.2f} ({fmt_p(logit6['adapted_p'])}) | {logit6['composite_or']:.2f} ({fmt_p(logit6['composite_p'])}) |
| Pro+Flash+Luna | {logit3['n']} | {logit3['hard3_or']:.2f} ({fmt_p(logit3['hard3_p'])}) | {logit3['adapted_or']:.2f} ({fmt_p(logit3['adapted_p'])}) | {logit3['composite_or']:.2f} ({fmt_p(logit3['composite_p'])}) |
| Five models, no GLM | {stats_blob['logit_five']['n']} | {stats_blob['logit_five']['hard3_or']:.2f} ({fmt_p(stats_blob['logit_five']['hard3_p'])}) | {stats_blob['logit_five']['adapted_or']:.2f} ({fmt_p(stats_blob['logit_five']['adapted_p'])}) | {stats_blob['logit_five']['composite_or']:.2f} ({fmt_p(stats_blob['logit_five']['composite_p'])}) |

Construction-split χ²: Pro Core {chi_pro['core_pass']}/{chi_pro['core_n']} vs hard3 {chi_pro['hard3_pass']}/{chi_pro['hard3_n']}, χ²={chi_pro['chi2']:.1f}, p={fmt_p(chi_pro['p'])}. Flash χ²={chi_flash['chi2']:.1f}, p={fmt_p(chi_flash['p'])}.

**Finding 4 (difficulty).** In-suite hard3 is the identifiable difficulty axis. After controlling for model and hard3, Composite is **not** significantly harder than Direct (strong-three OR={logit3['composite_or']:.2f}, p={fmt_p(logit3['composite_p'])}; six-model p={fmt_p(logit6['composite_p'])}). Adapted is likewise non-significant. The apparent Direct → Adapted → Composite gradient is confounded with construction split and is not supported as an independent benchmark finding.

**Can write.** Full 0/6–6/6 spectrum with a hard tail; Core-100 vs hard3 as the difficulty claim on Pro/Flash/Luna/GLM/Qwen; χ² / logistic hard3 effect; lift-type cells as descriptive, with n.

**Cannot write.** Direct → Adapted → Composite as a deconfounded finding. Official Hard-50 as the paper difficulty claim. Entanglement-level effects (uniformly high). A hard3 gap for OSS (25/100 vs 11/50, χ² p=0.84).

---

## RQ3 Failure stage / contract closure

### First failure (exclusive) — Table 2 in the manuscript

See `fig/fig_failure_stage_funnel.pdf`. Isolation-first is rare (Flash 1, GLM 2, OSS 1).

### Independent gates among delivered packages (non-exclusive)

| Model | Usable | Build fail | Public fail | Hidden fail | Isolation fail | Isolation \\| Build | Isolation-only after behavior |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Pro | {gates['Pro']['usable']} | {gates['Pro']['build_fail']} | {gates['Pro']['public_fail']} | {gates['Pro']['hidden_fail']} | {gates['Pro']['isolation_fail']} | {gates['Pro']['isolation_fail_given_build']} | {gates['Pro']['isolation_fail_given_behavior']} |
| Flash | {gates['Flash']['usable']} | {gates['Flash']['build_fail']} | {gates['Flash']['public_fail']} | {gates['Flash']['hidden_fail']} | {gates['Flash']['isolation_fail']} | {gates['Flash']['isolation_fail_given_build']} | {gates['Flash']['isolation_fail_given_behavior']} |
| Luna | {gates['Luna']['usable']} | {gates['Luna']['build_fail']} | {gates['Luna']['public_fail']} | {gates['Luna']['hidden_fail']} | {gates['Luna']['isolation_fail']} | {gates['Luna']['isolation_fail_given_build']} | {gates['Luna']['isolation_fail_given_behavior']} |
| GLM | {gates['GLM']['usable']} | {gates['GLM']['build_fail']} | {gates['GLM']['public_fail']} | {gates['GLM']['hidden_fail']} | {gates['GLM']['isolation_fail']} | {gates['GLM']['isolation_fail_given_build']} | {gates['GLM']['isolation_fail_given_behavior']} |
| Qwen | {gates['Qwen']['usable']} | {gates['Qwen']['build_fail']} | {gates['Qwen']['public_fail']} | {gates['Qwen']['hidden_fail']} | {gates['Qwen']['isolation_fail']} | {gates['Qwen']['isolation_fail_given_build']} | {gates['Qwen']['isolation_fail_given_behavior']} |
| OSS | {gates['OSS']['usable']} | {gates['OSS']['build_fail']} | {gates['OSS']['public_fail']} | {gates['OSS']['hidden_fail']} | {gates['OSS']['isolation_fail']} | {gates['OSS']['isolation_fail_given_build']} | {gates['OSS']['isolation_fail_given_behavior']} |

Figure: `fig/fig_independent_gates.pdf`.

**Finding 2.** Functional failures concentrate at the behavioral gates.

**Independence finding.** Isolation failures remain rare even when counted independently of first-failure. Raw isolation-fail among delivered packages is {iso_raw} across six models × 150 tasks; the binding residual (build ∧ public ∧ hidden pass, isolation fail) is **{iso_residual}**. Pro 0/150 raw and residual. Flash residual 1. Luna residual 0 (its 3 raw isolation fails co-occur with build fail). OSS raw isolation 22, but residual 1. **Independence is rarely the binding constraint; preserving complete behavior is.**

**Finding 3 (unchanged).** On the Pro+Flash artifact-fail slice, L1 close-read (n=63 valid agent rows) is dominated by incomplete recovery of the required behavioral contract rather than missing packages or uninspected source trees. Assistant first pass, not gold. Do not pool GLM/Qwen/OSS into that 63.

**Cannot write.** Isolation is easy *only* because first-failure isolation is ~0, without the independent table. A five-model semantic pie. Gold taxonomy.

---

## RQ4 Correctness vs compactness

Pro vs Luna, same-task functional passes, n={pl['n']}:

- median copy Pro {pl['median_a']:.3f} vs Luna {pl['median_b']:.3f} (difference of medians {pl['median_a']-pl['median_b']:.3f})
- median paired difference (Pro−Luna) {pl['median_diff']:.3f} (not equal to the difference of medians; Luna is mixed compact / copy-heavy)
- Wilcoxon signed-rank p={fmt_p(pl['wilcoxon_p'])}
- matched-pairs rank-biserial r={pl['rank_biserial']:.3f}
- Pro greater copy on {pl['n_a_greater']}/{pl['n']} tasks; Luna greater on {pl['n_b_greater']}; ties {pl['n_tie']}
- paired RRES medians {pl['rres_median_a']:.3f} vs {pl['rres_median_b']:.3f}

Flash vs Luna, n={fl['n']}: median copy {fl['median_a']:.3f} vs {fl['median_b']:.3f}, median paired difference {fl['median_diff']:.3f}, Wilcoxon p={fmt_p(fl['wilcoxon_p'])}, r={fl['rank_biserial']:.3f}. Flash greater copy on {fl['n_a_greater']}/{fl['n']}.

Figure: `fig/fig_paired_copy.pdf`.

**Finding 5.** Comparable functional success conceals systematically different extraction strategies. Pro (and Flash) passing packages are copy-heavy; Luna copies substantially less on the same tasks.

**Can write.** Paired, not unpaired, compactness; survivor sets differ. Wilcoxon + rank-biserial on the n={pl['n']} intersection.

**Cannot write.** Luna is “better” because copy is lower. Compactness as a second ranking of the 150. Unpaired medians as if they were the same 150 tasks.

---

## RQ5 Efficiency (appendix)

Token field: Pro/Flash = incremental (uncached prompt + completion). Qwen/OSS = summed provider total_tokens (no cache ledger). Luna/GLM = missing token fields (`usage_unverified`); steps and duration only.

| Model | Pass | Median tokens | P90 tokens | Median steps | n with tokens |
| --- | ---: | ---: | ---: | ---: | ---: |
{tok_lines}

Core vs hard3 and pass vs fail: `fig/fig_token_efficiency.pdf`, `csv/token_core_hard3.csv`, `csv/token_pass_fail.csv`.

On Pro, hard3 median incremental tokens {pro_hard_h:.0f} vs Core {pro_core_h:.0f} (Mann–Whitney p={fmt_p(pro_core_p)}); Pro hard3 pass is still 21/50 vs 94/100 on Core. Flash: 203k vs 108k incremental (p={fmt_p(next(t.get('core_vs_hard3_p') for t in tok['tests'] if t['model']=='Flash'))}), hard3 pass 18/50 vs 90/100. **Additional interaction budget alone does not eliminate the hard-tail gap.**

Qwen/OSS use a different token ledger (`total_tokens`, no cache accounting) and must not be plotted on the same axis as Pro/Flash. Luna/GLM have no token fields.

**Cannot write.** Dollar cost. Luna/GLM token rankings. `total_tokens` for Pro/Flash as billed usage. A four-model token chart that mixes incremental and total.

---

## P2. Pro vs Flash discordant tasks

Pro wins {disc['pro_wins_tally']['n']}, Flash wins {disc['flash_wins_tally']['n']}, McNemar p={fmt_p(stats_blob['mcnemar_pro_flash']['p'])} (not a significant overall advantage).

Pro-only passes ({disc['pro_wins_tally']['n']}): hard3 {disc['pro_wins_tally']['hard3']}/{disc['pro_wins_tally']['n']}; lift {fmt_count(disc['pro_wins_tally']['lift'])}. Flash first-failure on those tasks is mostly Hidden ({fmt_count(disc['pro_wins_tally']['flash_stage'])}). Flash L1 primary cause {fmt_count(disc['pro_wins_tally']['flash_cause'])}.

Flash-only passes ({disc['flash_wins_tally']['n']}): **all hard3**; lift {fmt_count(disc['flash_wins_tally']['lift'])}. Pro first-failure {fmt_count(disc['flash_wins_tally']['pro_stage'])}; Pro L1 {fmt_count(disc['flash_wins_tally']['pro_cause'])}.

**P2 takeaway.** Pro does not mainly rescue Composite (2/10). It mainly recovers additional **behavioral** failures (Hidden/Public; L1 drift or incomplete API), 6/10 of them on hard3. Flash’s 3 counterexamples are also hard3 behavioral misses by Pro. Descriptive only; do not upgrade to a model-class theory.

See `csv/pro_flash_discordant.csv`.

---

## Paper figure/table map

| Paper | File |
| --- | --- |
| Table 1 capability | already in manuscript; numbers above |
| Figure 1 funnel | `fig/fig_failure_stage_funnel.pdf` |
| Figure 2 difficulty spectrum | `fig/fig_task_difficulty_spectrum.pdf` |
| Figure/Table 3 lift × hard3 | `fig/fig_lift_type_hard3.pdf`, `csv/lift_type_hard3.csv` |
| Figure 4 paired copy | `fig/fig_paired_copy.pdf` |
| Table 5 semantic L1 | existing F3 CSV; do not restyle as gold |
| Independent gates | `fig/fig_independent_gates.pdf` |
| Appendix efficiency | `fig/fig_token_efficiency.pdf` |

Python-150 main experiments can freeze here. No new models, methods, or leaderboard columns.

---

## Copy into the manuscript (English)

**F1.** Current coding agents exhibit substantial but incomplete feature-lifting capability on frozen Python-150, with large performance differences across model backends (24.0%–76.7%). The strongest backend still fails 35/150 tasks; {unsolved6['total']} tasks are unsolved by every backend.

**F2.** Functional failures concentrate at the behavioral gates. Among delivered packages, independent isolation failure after passing build, public, and hidden checks occurs only {iso_residual} times across six models × 150 tasks. Independence is rarely the binding constraint; preserving complete behavior is.

**F3.** On the Pro+Flash artifact-fail slice (n=63 valid agent rows), L1 close-read is dominated by incomplete recovery of the required behavioral contract rather than by missing packages or uninspected source trees. This remains an assistant-first-pass analysis, not a gold taxonomy.

**F4.** Feature-lifting difficulty on Python-150 is identified by the in-suite hard3 construction split (Pro 94/100 vs 21/50). After controlling for model and hard3, Composite is not significantly harder than Direct (OR={logit3['composite_or']:.2f}, p={fmt_p(logit3['composite_p'])}). The apparent Direct → Adapted → Composite gradient is confounded with construction-split composition (Composite is 15/18 hard3; Direct is 53/56 Core) and is not an independent benchmark finding.

**F5.** Comparable functional success conceals systematically different extraction strategies. On the {pl['n']} tasks passed by both Pro and Luna, median copy fraction is {pl['median_a']:.3f} vs {pl['median_b']:.3f} (Wilcoxon p={fmt_p(pl['wilcoxon_p'])}, matched-pairs rank-biserial r={pl['rank_biserial']:.2f}).
"""
    (HERE / "summary_rq.md").write_text(text, encoding="utf-8")


def mcnemar_from_rows(rows: list[dict[str, Any]], a: str, b: str) -> dict[str, Any]:
    pa = {r["task_id"]: r["functional_pass"] for r in rows if r["model"] == a}
    pb = {r["task_id"]: r["functional_pass"] for r in rows if r["model"] == b}
    n10 = n01 = 0
    for tid in pa:
        if pa[tid] and not pb[tid]:
            n10 += 1
        elif pb[tid] and not pa[tid]:
            n01 += 1
    n = n01 + n10
    if n == 0:
        p = 1.0
    else:
        k = min(n01, n10)
        p = 0.0
        for i in range(0, k + 1):
            p += math.comb(n, i)
        p = min(1.0, 2 * p / (2 ** n))
    return {"a": SHORT[a], "b": SHORT[b], "n10": n10, "n01": n01, "p": p}


def leaderboard_blob(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    grouped = by_model(rows)
    for key, short in MODELS:
        items = grouped[key]
        passed = sum(1 for r in items if r["functional_pass"])
        empty = sum(1 for r in items if not r["usable_submission"])
        core = [r for r in items if not r["hard3"]]
        hard = [r for r in items if r["hard3"]]
        lo, hi = wilson(passed, 150)
        out.append(
            {
                "short": short,
                "display": f"{passed}/150 ({100*passed/150:.1f}%)",
                "passed": passed,
                "wilson": f"{100*lo:.1f}–{100*hi:.1f}%",
                "core": rate(sum(1 for r in core if r["functional_pass"]), 100),
                "hard3": rate(sum(1 for r in hard if r["functional_pass"]), 50),
                "empty": empty,
            }
        )
    return out


def write_tex(stats_blob: dict[str, Any]) -> None:
    path = HERE / "tex" / "tables.tex"
    path.parent.mkdir(parents=True, exist_ok=True)
    spec = stats_blob["spectrum6"]
    lb = stats_blob["leaderboard"]
    gates = stats_blob["independent_gates"]
    pl = stats_blob["paired_pro_luna"]
    fl = stats_blob["paired_flash_luna"]
    logit3 = stats_blob["logit_strong3"]
    compact = {r["label"]: r for r in stats_blob.get("pass_compactness", [])}
    tok = {r["label"]: r for r in stats_blob.get("token", {}).get("by_model", [])}

    def esc(s: str) -> str:
        return s.replace("%", "\\%")

    lines = [
        "% Auto-generated from python150_paper_analysis_final/build.py",
        "% Python-150 freeze v2. Functional Pass = build /\\ public /\\ hidden /\\ isolation.",
        "",
        "% Table 1 — Main capability",
        "\\begin{tabular}{lrrrrr}",
        "\\hline",
        "Model & Pass & 95\\% CI & Core-100 & hard3 & Empty \\\\",
        "\\hline",
    ]
    for r in lb:
        lines.append(
            f"{r['short']} & {esc(r['display'])} & {esc(r['wilson'])} & {esc(r['core'])} & {esc(r['hard3'])} & {r['empty']} \\\\"
        )
    lines += ["\\hline", "\\end{tabular}", ""]
    if compact:
        lines += [
            "% Pass-conditioned compactness (Functional Pass artifacts only)",
            "\\begin{tabular}{lrrrrrrrrr}",
            "\\hline",
            "Model & $n$ & Mean RRES & Median RRES & IQR RRES & Mean copy & Median copy & IQR copy \\\\",
            "\\hline",
        ]
        for r in lb:
            c = compact[r["short"]]
            lines.append(
                f"{r['short']} & {c['n_pass']} & {c['rres_mean']:.3f} & {c['rres_median']:.3f} & "
                f"[{c['rres_q1']:.3f}, {c['rres_q3']:.3f}] & "
                f"{c['copy_mean']:.3f} & {c['copy_median']:.3f} & "
                f"[{c['copy_q1']:.3f}, {c['copy_q3']:.3f}] \\\\"
            )
        lines += ["\\hline", "\\end{tabular}", ""]
    lines += [
        "\\begin{tabular}{lrrr}",
        "\\hline",
        "Solved & Core-100 & hard3 & Total \\\\",
        "\\hline",
    ]
    for b in spec["bins"]:
        lines.append(f"{b['label']} & {b['core100']} & {b['hard3']} & {b['total']} \\\\")
    lines += ["\\hline", "\\end{tabular}", ""]
    lines += [
        "% Lift-type inventory (confounder)",
        "\\begin{tabular}{lrrrr}",
        "\\hline",
        "Split & Direct & Adapted & Composite & Total \\\\",
        "\\hline",
        f"Core-100 & {inv['core100']['Direct']} & {inv['core100']['Adapted']} & {inv['core100']['Composite']} & {inv['core100']['n_tasks']} \\\\",
        f"hard3 & {inv['hard3']['Direct']} & {inv['hard3']['Adapted']} & {inv['hard3']['Composite']} & {inv['hard3']['n_tasks']} \\\\",
        "\\hline",
        "\\end{tabular}",
        "",
        "% Independent gates (non-exclusive, delivered packages)",
        "\\begin{tabular}{lrrrrrr}",
        "\\hline",
        "Model & Usable & Build fail & Public fail & Hidden fail & Isolation fail & Isolation residual \\\\",
        "\\hline",
    ]
    for g in gates:
        lines.append(
            f"{g['label']} & {g['usable']} & {g['build_fail']} & {g['public_fail']} & {g['hidden_fail']} & {g['isolation_fail']} & {g['isolation_fail_given_behavior']} \\\\"
        )
    lines += [
        "\\hline",
        "\\end{tabular}",
        "",
        "% Paired compactness Pro vs Luna",
        "\\begin{tabular}{lrr}",
        "\\hline",
        f" & Pro & Luna \\\\",
        "\\hline",
        f"$n$ jointly passing & \\multicolumn{{2}}{{c}}{{{pl['n']}}} \\\\",
        f"Median copy fraction & {pl['median_a']:.3f} & {pl['median_b']:.3f} \\\\",
        f"Median paired difference (Pro$-$Luna) & \\multicolumn{{2}}{{c}}{{{pl['median_diff']:.3f}}} \\\\",
        f"Wilcoxon $p$ & \\multicolumn{{2}}{{c}}{{{fmt_p(pl['wilcoxon_p'])}}} \\\\",
        f"Rank-biserial $r$ & \\multicolumn{{2}}{{c}}{{{pl['rank_biserial']:.3f}}} \\\\",
        "\\hline",
        "\\end{tabular}",
        "",
        f"% Logistic strong3: Composite OR={logit3['composite_or']:.2f}, p={fmt_p(logit3['composite_p'])}; hard3 OR={logit3['hard3_or']:.2f}",
        f"% Flash vs Luna n={fl['n']}, Wilcoxon p={fmt_p(fl['wilcoxon_p'])}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = load_task_results()
    f3 = load_f3()
    (HERE / "csv").mkdir(parents=True, exist_ok=True)
    (HERE / "json").mkdir(parents=True, exist_ok=True)
    (HERE / "fig").mkdir(parents=True, exist_ok=True)

    diff6 = task_difficulty_table(rows, MODEL_KEYS)
    diff5 = task_difficulty_table(rows, FIVE_NO_GLM)
    save_csv(HERE / "csv" / "task_difficulty.csv", diff6)
    save_csv(HERE / "csv" / "task_difficulty_5model.csv", diff5)
    spec6 = spectrum_counts(diff6, 6)
    spec5 = spectrum_counts(diff5, 5)
    plot_spectrum(spec6, "fig_task_difficulty_spectrum", "Models solving each Python-150 task")
    plot_spectrum(spec5, "fig_task_difficulty_spectrum_5model", "Models solving each task (5 backends, no GLM)")

    lift_cells = []
    for key in MODEL_KEYS + [None]:
        lift_cells.extend(lift_hard3_cells(rows, key))
    five_rows = [r for r in rows if r["model"] in FIVE_NO_GLM]
    five_pooled = lift_hard3_cells(five_rows, None)
    for rec in five_pooled:
        rec["model"] = "pooled_five"
        rec["label"] = "pooled_five"
    lift_cells.extend(five_pooled)
    save_csv(HERE / "csv" / "lift_type_hard3.csv", lift_cells)
    inv = lift_inventory(rows)
    save_csv(HERE / "csv" / "lift_inventory.csv", inv)
    plot_lift_hard3(lift_cells)
    chi2_rows = [construction_chi2(rows, k) for k, _ in MODELS]
    save_csv(HERE / "csv" / "construction_chi2.csv", chi2_rows)

    import pandas as pd  # noqa: F401  # statsmodels formula API

    logit_all6 = fit_logit(rows, MODEL_KEYS, "all6")
    logit_strong3 = fit_logit(rows, STRONG3, "strong3")
    logit_five = fit_logit(rows, FIVE_NO_GLM, "five_no_glm")
    (HERE / "csv" / "logistic_params.csv").parent.mkdir(parents=True, exist_ok=True)
    save_csv(
        HERE / "csv" / "logistic_params.csv",
        [{**p, "fit": logit_all6["tag"]} for p in logit_all6["params"]]
        + [{**p, "fit": logit_strong3["tag"]} for p in logit_strong3["params"]]
        + [{**p, "fit": logit_five["tag"]} for p in logit_five["params"]],
    )

    pro_luna = paired_compactness(rows, "deepseek-v4-pro", "gpt-5.6-luna")
    flash_luna = paired_compactness(rows, "deepseek-v4-flash", "gpt-5.6-luna")
    save_csv(HERE / "csv" / "paired_copy_pro_luna.csv", pro_luna["pairs"])
    save_csv(HERE / "csv" / "paired_copy_flash_luna.csv", flash_luna["pairs"])
    plot_paired_copy(pro_luna, flash_luna)

    gates = independent_gates(rows)
    save_csv(HERE / "csv" / "independent_gates.csv", gates)
    plot_independent_gates(gates)
    plot_funnel(rows)

    tok = token_tables(rows)
    save_csv(HERE / "csv" / "token_by_model.csv", tok["by_model"])
    save_csv(HERE / "csv" / "token_core_hard3.csv", tok["core_hard3"])
    save_csv(HERE / "csv" / "token_pass_fail.csv", tok["pass_fail"])
    plot_token_efficiency(tok)

    compact = pass_compactness(rows)
    save_csv(HERE / "csv" / "pass_compactness.csv", compact)

    disc = discordant_pro_flash(rows, f3)
    save_csv(HERE / "csv" / "pro_flash_discordant.csv", disc["pro_wins"] + disc["flash_wins"])

    stats_blob = {
        "n_rows": len(rows),
        "leaderboard": leaderboard_blob(rows),
        "spectrum6": spec6,
        "spectrum5": spec5,
        "construction_chi2": chi2_rows,
        "lift_inventory": inv,
        "lift_hard3": lift_cells,
        "logit_all6": {k: v for k, v in logit_all6.items() if k != "summary_text"},
        "logit_strong3": {k: v for k, v in logit_strong3.items() if k != "summary_text"},
        "logit_five": {k: v for k, v in logit_five.items() if k != "summary_text"},
        "logit_all6_text": logit_all6["summary_text"],
        "logit_strong3_text": logit_strong3["summary_text"],
        "paired_pro_luna": {k: v for k, v in pro_luna.items() if k != "pairs"},
        "paired_flash_luna": {k: v for k, v in flash_luna.items() if k != "pairs"},
        "independent_gates": gates,
        "token": tok,
        "pass_compactness": compact,
        "pro_flash_discordant": {
            "pro_wins_tally": disc["pro_wins_tally"],
            "flash_wins_tally": disc["flash_wins_tally"],
        },
        "mcnemar_pro_flash": mcnemar_from_rows(rows, "deepseek-v4-pro", "deepseek-v4-flash"),
        "mcnemar_pro_luna": mcnemar_from_rows(rows, "deepseek-v4-pro", "gpt-5.6-luna"),
        "mcnemar_glm_qwen": mcnemar_from_rows(rows, "glm-5.3-flash", "qwen3.6-35b-a3b-fp8"),
    }
    (HERE / "json" / "stats.json").write_text(
        json.dumps(stats_blob, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    (HERE / "json" / "logit_strong3.txt").write_text(logit_strong3["summary_text"] + "\n", encoding="utf-8")
    (HERE / "json" / "logit_all6.txt").write_text(logit_all6["summary_text"] + "\n", encoding="utf-8")
    write_tex(stats_blob)
    # summary_final.md is the frozen data dump; RQ notes go to summary_rq.md.
    write_summary(stats_blob)
    (HERE / "README.md").write_text(
        """# Python-150 paper analysis final

Freeze v2 Official Main 收尾包。不再跑模型、不造方法。输入是
`../python150_prime_v2_analysis_20260905/task_results.csv`。

```bash
.venv/bin/python reports/paper_analysis/python150_paper_analysis_final/build.py
```

先读 `summary_final.md`（按 RQ：数字 → 检验 → Finding → 能写/不能写）。

| 路径 | 内容 |
| --- | --- |
| `summary_final.md` | 论文可抄写的 RQ 结论 |
| `fig/fig_task_difficulty_spectrum.pdf` | Figure 2：0/6–6/6，Core/hard3 stacked |
| `fig/fig_paired_copy.pdf` | Figure 4：Pro vs Luna 同题 copy |
| `fig/fig_independent_gates.pdf` | 非互斥四门失败 |
| `fig/fig_failure_stage_funnel.pdf` | Figure 1：首败漏斗 |
| `fig/fig_lift_type_hard3.pdf` | Lift × hard3（注明小 n） |
| `fig/fig_token_efficiency.pdf` | 附录：Pro/Flash incremental |
| `csv/task_difficulty.csv` | 每题 6 模型 pass 与 `num_models_solved` |
| `csv/lift_inventory.csv` | Direct/Adapted/Composite × Core/hard3 题数 |
| `csv/logistic_params.csv` | `passed ~ model + hard3 + lift_type` |
| `tex/tables.tex` | 可粘贴的 LaTeX 表 |
| `json/stats.json` | 全部统计 |

**不要**把控制 hard3 后的 Composite 写成显著更难。**不要**把 F3 的 63 升级成金标。
""",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "out": str(HERE),
                "spectrum6_unsolved": spec6["unsolved_total"],
                "spectrum6_all": spec6["all_solved"],
                "logit3_composite_or": logit_strong3["composite_or"],
                "logit3_composite_p": logit_strong3["composite_p"],
                "logit3_hard3_or": logit_strong3["hard3_or"],
                "paired_n": pro_luna["n"],
                "paired_p": pro_luna["wilcoxon_p"],
                "paired_r": pro_luna["rank_biserial"],
                "flash_iso_ind": next(g["isolation_fail"] for g in gates if g["label"] == "Flash"),
                "pro_iso_ind": next(g["isolation_fail"] for g in gates if g["label"] == "Pro"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
