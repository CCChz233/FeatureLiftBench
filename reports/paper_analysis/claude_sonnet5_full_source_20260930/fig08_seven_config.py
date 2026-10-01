#!/usr/bin/env python3
"""Seven-configuration task fixed effects for successful artifacts.

Same estimator as docs/paper-workbench/figures/scripts/footprint_analysis.py.
The six-model sample is checked against the published point estimates, then
Claude is added and the model is refit. Adding a configuration changes the
sum-to-zero center, so these coefficients are not the six-model table.
"""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.linalg import lstsq

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "docs/paper-workbench"))
from paper_inputs import MODELS, RESULTS, paper_tasks, read_csv  # noqa: E402

HERE = Path(__file__).resolve().parent
CLAUDE_ARTIFACTS = HERE / "fig08_artifacts.csv"
OUT = HERE / "fig08_seven"
REPLICATES = 10_000
SEED = 20260915
SIX = tuple(MODELS)
SEVEN = SIX + ("claude-sonnet-5",)
SHORT = {
    "deepseek-v4-pro": "Pro",
    "deepseek-v4-flash": "Flash",
    "gpt-5.6-luna": "Luna",
    "glm-5.3-flash": "GLM",
    "qwen3.6-35b-a3b-fp8": "Qwen",
    "gpt-oss-120b": "OSS",
    "claude-sonnet-5": "Claude",
}
PUBLISHED_TASK_BOOTSTRAP = {
    "Pro": (1.178, 15.42),
    "Flash": (1.314, 16.81),
    "Luna": (0.612, -20.64),
    "GLM": (1.555, 14.20),
    "Qwen": (1.109, -1.79),
    "OSS": (0.612, -24.00),
}


def connected(information: np.ndarray) -> bool:
    adjacency = information < -1e-10
    seen, pending = {0}, [0]
    while pending:
        for node in np.flatnonzero(adjacency[pending.pop()]):
            node = int(node)
            if node not in seen:
                seen.add(node)
                pending.append(node)
    return len(seen) == information.shape[0]


def solve(information: np.ndarray, rhs: np.ndarray) -> np.ndarray:
    if not connected(information):
        raise ValueError("Disconnected configuration comparison graph")
    width = information.shape[0]
    beta = np.linalg.solve(information + np.ones((width, width)) / width, rhs)
    beta -= beta.mean(axis=0)
    if not np.isfinite(beta).all() or not np.allclose(information @ beta, rhs, atol=1e-8):
        raise RuntimeError("Fixed-effect solution failed the normal equations")
    return beta


def dense_verification(blocks: list[dict], beta: np.ndarray, task_equal: bool) -> float:
    width = beta.shape[0]
    contrast = np.vstack((np.eye(width - 1), -np.ones(width - 1)))
    design, outcome, weights = [], [], []
    for task_index, block in enumerate(blocks):
        task_dummy = np.zeros((block["k"], len(blocks)))
        task_dummy[:, task_index] = 1
        design.append(np.column_stack((task_dummy, block["X"] @ contrast)))
        outcome.append(block["Y"])
        weights.extend([1 / block["k"] if task_equal else 1] * block["k"])
    root = np.sqrt(weights)[:, None]
    estimate, _, rank, _ = lstsq(np.vstack(design) * root, np.vstack(outcome) * root)
    if rank != len(blocks) + width - 1:
        raise RuntimeError(f"dense rank {rank} != {len(blocks) + width - 1}")
    recovered = contrast @ estimate[-(width - 1) :]
    error = float(np.max(np.abs(recovered - beta)))
    if error >= 1e-8:
        raise RuntimeError(f"within estimates differ from explicit fixed effects: {error}")
    return error


def load_successes(models: tuple[str, ...]) -> list[dict]:
    release = paper_tasks()
    rows = []
    for row in read_csv(RESULTS):
        if row["model"] not in models or row["functional_pass"] != "True":
            continue
        rows.append(
            {
                "task_id": row["task_id"],
                "model": row["model"],
                "lift_type": row["lift_type"],
                "repository": release[row["task_id"]]["source_repo_id"],
                "rres": float(row["rres"]),
                "copied_fraction": float(row["copied_fraction"]),
            }
        )
    if "claude-sonnet-5" in models:
        with CLAUDE_ARTIFACTS.open(newline="") as handle:
            claude = list(csv.DictReader(handle))
        if len(claude) != 89:
            raise SystemExit(f"expected 89 Claude successes, got {len(claude)}")
        for row in claude:
            if row["task_id"] not in release:
                raise SystemExit(f"Claude task outside the 150: {row['task_id']}")
            rows.append(
                {
                    "task_id": row["task_id"],
                    "model": "claude-sonnet-5",
                    "lift_type": row["lift_type"],
                    "repository": release[row["task_id"]]["source_repo_id"],
                    "rres": float(row["rres"]),
                    "copied_fraction": float(row["copied_fraction"]),
                }
            )
    return rows


def build_blocks(rows: list[dict], models: tuple[str, ...]) -> tuple[list[dict], dict]:
    success: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        if not (row["rres"] > 0 and 0 <= row["copied_fraction"] <= 1):
            raise SystemExit(f"invalid footprint {row['model']} {row['task_id']}")
        success[row["task_id"]].append(row)
    included = {task: group for task, group in sorted(success.items()) if len(group) >= 2}
    width = len(models)
    overlap = np.zeros((width, width), dtype=int)
    blocks = []
    observations = []
    for task, group in included.items():
        group = sorted(group, key=lambda row: models.index(row["model"]))
        index = [models.index(row["model"]) for row in group]
        overlap[np.ix_(index, index)] += 1
        raw = np.array([[row["rres"], row["copied_fraction"]] for row in group])
        design = np.eye(width)[index]
        outcome = np.column_stack((np.log2(raw[:, 0]), raw[:, 1]))
        centered_x = design - design.mean(axis=0)
        centered_y = outcome - outcome.mean(axis=0)
        blocks.append(
            {
                "task_id": task,
                "repository": group[0]["repository"],
                "k": len(group),
                "X": design,
                "Y": outcome,
                "A": centered_x.T @ centered_x,
                "B": centered_x.T @ centered_y,
            }
        )
        for row, values in zip(group, raw):
            observations.append({**row, "rres": float(values[0]), "copied_fraction": float(values[1])})
    sample = {
        "models": list(models),
        "tasks": len(included),
        "artifacts": len(observations),
        "repositories": len({block["repository"] for block in blocks}),
        "all_successes": sum(map(len, success.values())),
        "singleton_successes_excluded": sum(len(group) == 1 for group in success.values()),
        "included_per_model": overlap.diagonal().tolist(),
        "pairwise_overlap": overlap.tolist(),
        "lift_types": dict(Counter(group[0]["lift_type"] for group in included.values())),
    }
    return blocks, sample


def bootstrap(information, rhs_blocks, replicates: int, seed: int):
    rng = np.random.default_rng(seed)
    draws = []
    rejected = 0
    attempts = 0
    while len(draws) < replicates:
        attempts += 1
        if attempts > replicates * 20:
            raise RuntimeError("Too many disconnected draws")
        multiplicity = np.bincount(rng.integers(len(information), size=len(information)), minlength=len(information))
        info = np.einsum("t,tij->ij", multiplicity, information)
        rhs = np.einsum("t,tij->ij", multiplicity, rhs_blocks)
        if not connected(info):
            rejected += 1
            continue
        draws.append(solve(info, rhs))
    return np.asarray(draws), {
        "accepted": replicates,
        "attempts": attempts,
        "disconnected_rejected": rejected,
        "seed": seed,
        "clusters": len(information),
    }


def fit(models: tuple[str, ...], replicates: int) -> dict:
    blocks, sample = build_blocks(load_successes(models), models)
    base_a = np.array([block["A"] for block in blocks])
    base_b = np.array([block["B"] for block in blocks])
    if np.linalg.matrix_rank(base_a.sum(axis=0)) != len(models) - 1:
        raise RuntimeError("within design is rank deficient")
    analyses = {}
    for name in ("task_bootstrap", "task_equal_weight", "repository_bootstrap"):
        task_equal = name == "task_equal_weight"
        weights = np.array([1 / block["k"] if task_equal else 1 for block in blocks])
        information = base_a * weights[:, None, None]
        rhs = base_b * weights[:, None, None]
        beta = solve(information.sum(axis=0), rhs.sum(axis=0))
        dense_error = None
        if name != "repository_bootstrap":
            dense_error = dense_verification(blocks, beta, task_equal)
        clustered_a, clustered_b = information, rhs
        if name == "repository_bootstrap":
            repositories = sorted({block["repository"] for block in blocks})
            membership = np.array([[block["repository"] == repo for block in blocks] for repo in repositories])
            clustered_a = np.einsum("rt,tij->rij", membership, information)
            clustered_b = np.einsum("rt,tij->rij", membership, rhs)
        draws, audit = bootstrap(
            clustered_a,
            clustered_b,
            replicates,
            SEED + int(name == "repository_bootstrap"),
        )
        quantiles = np.quantile(draws, [0.025, 0.975], axis=0, method="linear")
        rows = []
        for index, model in enumerate(models):
            rows.append(
                {
                    "model": model,
                    "short": SHORT[model],
                    "included_success_n": sample["included_per_model"][index],
                    "rres_ratio": float(2 ** beta[index, 0]),
                    "rres_ci": (2 ** quantiles[:, index, 0]).tolist(),
                    "copy_pp": float(100 * beta[index, 1]),
                    "copy_ci": (100 * quantiles[:, index, 1]).tolist(),
                }
            )
        analyses[name] = {
            "weighting": "1/k_t per artifact" if task_equal else "equal artifact weight",
            "cluster": "repository" if name == "repository_bootstrap" else "task",
            "dense_max_error": dense_error,
            "bootstrap": audit,
            "rows": rows,
        }
    return {"sample": sample, "analyses": analyses}


def check_six() -> None:
    fitted = fit(SIX, replicates=200)
    rows = {row["short"]: row for row in fitted["analyses"]["task_bootstrap"]["rows"]}
    for short, (ratio, copy) in PUBLISHED_TASK_BOOTSTRAP.items():
        if abs(rows[short]["rres_ratio"] - ratio) > 0.0015 or abs(rows[short]["copy_pp"] - copy) > 0.02:
            raise SystemExit(f"six-model point estimate drifted for {short}: {rows[short]}")
    sample = fitted["sample"]
    if (sample["tasks"], sample["artifacts"], sample["repositories"]) != (115, 485, 97):
        raise SystemExit(f"six-model sample drifted: {sample}")
    print("six-model point estimates match the published table", flush=True)


def write_seven(payload: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "fig08_seven_analysis.json").write_text(json.dumps(payload, indent=2) + "\n")
    columns = [
        "configuration",
        "included_success_n",
        "rres_ratio",
        "rres_ci_low",
        "rres_ci_high",
        "copy_pp",
        "copy_ci_low",
        "copy_ci_high",
    ]
    sample = payload["sample"]
    lines = [
        "# Seven-configuration task-adjusted footprint",
        "",
        f"{sample['tasks']} tasks; {sample['artifacts']} successful artifacts; {sample['repositories']} repositories.",
        "Configurations stay in the published order, with Claude Sonnet 5 appended.",
        "Coefficients are centered to sum to zero across these seven configurations.",
        "They are not the six-configuration coefficients. Success-conditional; failed runs are not filled with zero.",
        f"Singletons excluded: {sample['singleton_successes_excluded']}. All successes before that filter: {sample['all_successes']}.",
        "",
    ]
    for name, analysis in payload["analyses"].items():
        audit = analysis["bootstrap"]
        path = OUT / f"fig08_seven_{name}.csv"
        with path.open("w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(columns)
            for row in analysis["rows"]:
                writer.writerow(
                    [
                        row["short"],
                        row["included_success_n"],
                        row["rres_ratio"],
                        *row["rres_ci"],
                        row["copy_pp"],
                        *row["copy_ci"],
                    ]
                )
        lines += [
            f"## {name}",
            "",
            f"{audit['accepted']:,} accepted draws; {audit['disconnected_rejected']} disconnected draws rejected; seed {audit['seed']}.",
            "",
            "| Configuration | Included n | RRES ratio [95% CI] | Copy pp [95% CI] |",
            "| --- | ---: | ---: | ---: |",
        ]
        for row in analysis["rows"]:
            lines.append(
                f"| {row['short']} | {row['included_success_n']} | "
                f"{row['rres_ratio']:.3f} [{row['rres_ci'][0]:.3f}, {row['rres_ci'][1]:.3f}] | "
                f"{row['copy_pp']:+.2f} [{row['copy_ci'][0]:+.2f}, {row['copy_ci'][1]:+.2f}] |"
            )
        lines.append("")
    (OUT / "fig08_seven_results.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    check_six()
    payload = fit(SEVEN, REPLICATES)
    write_seven(payload)
    sample = payload["sample"]
    print(
        f"seven tasks={sample['tasks']} artifacts={sample['artifacts']} repos={sample['repositories']}",
        flush=True,
    )
    for row in payload["analyses"]["task_bootstrap"]["rows"]:
        print(
            f"{row['short']} n={row['included_success_n']} "
            f"rres={row['rres_ratio']:.3f} copy={row['copy_pp']:+.2f}",
            flush=True,
        )


if __name__ == "__main__":
    main()
