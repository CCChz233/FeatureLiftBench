#!/usr/bin/env python3
"""Paired Full Source vs Contract Only outcomes for Claude Sonnet 5.

Functional pass is Build and Primary and Extended and Isolation.
The bootstrap and exact McNemar follow the retained-ablation script.
Holm is recomputed across Luna, Pro, Qwen, and Claude.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
FULL = ROOT / "experiments/python/openhands/claude-sonnet-5/python150-main-r1"
CONTRACT = ROOT / "experiments/python/openhands/claude-sonnet-5/python150-contract-only-r1"
TASKS = ROOT / "reports/paper_analysis/claude_sonnet5_full_source_20260930/task_results.csv"
SEED = 20260913
RESAMPLES = 100_000
# Discordant counts already reported for the 150-task table.
PUBLISHED = [
    {"configuration": "GPT-5.6 Luna", "full_only": 56, "contract_only": 8},
    {"configuration": "DeepSeek V4 Pro", "full_only": 88, "contract_only": 4},
    {"configuration": "Qwen3.6-35B-A3B", "full_only": 59, "contract_only": 3},
]


def gates(result: dict) -> dict[str, bool]:
    isolation = result.get("isolation") or {}
    return {
        "build_pass": result.get("build_pass") is True,
        "public_pass": result.get("public_tests_pass") is True,
        "hidden_pass": result.get("hidden_tests_pass") is True,
        "isolation_pass": isolation.get("pass") is True,
    }


def first_stage(flags: dict[str, bool]) -> str:
    if all(flags.values()):
        return "functional_pass"
    for name, key in (
        ("build_failure", "build_pass"),
        ("public_failure", "public_pass"),
        ("hidden_failure", "hidden_pass"),
        ("isolation_failure", "isolation_pass"),
    ):
        if not flags[key]:
            return name
    return "functional_pass"


def load_arm(root: Path, task_id: str) -> dict:
    result_path = root / task_id / "eval" / "result.json"
    result = json.loads(result_path.read_text())
    flags = gates(result)
    passed = all(flags.values())
    recorded = (result.get("scores") or {}).get("functional_gate")
    if recorded not in (0, 0.0, 1, 1.0) or bool(recorded) != passed:
        raise SystemExit(f"functional_gate mismatch {root.name} {task_id}: {recorded} vs {passed}")
    return {
        "pass": int(passed),
        "stage": first_stage(flags),
        "capsule": result.get("evaluation_capsule_digest") or "",
        **flags,
    }


def exact_p(full_only: int, contract_only: int) -> float:
    discord = full_only + contract_only
    if discord == 0:
        return 1.0
    return float(binomtest(full_only, discord, 0.5, alternative="two-sided").pvalue)


def holm(rows: list[dict]) -> None:
    running = 0.0
    ordered = sorted(rows, key=lambda row: row["mcnemar_exact_p"])
    family = len(ordered)
    for index, row in enumerate(ordered):
        running = max(running, min(1.0, (family - index) * row["mcnemar_exact_p"]))
        row["holm_p"] = running


def bootstrap(delta: np.ndarray, repositories: list[str]) -> dict:
    rng = np.random.default_rng(SEED)
    task_draws = delta[rng.integers(0, len(delta), size=(RESAMPLES, len(delta)))].mean(axis=1)
    task_ci = (100 * np.quantile(task_draws, [0.025, 0.975])).tolist()
    repos = sorted(set(repositories))
    sums = np.array([delta[np.array(repositories) == repo].sum() for repo in repos])
    sizes = np.array([(np.array(repositories) == repo).sum() for repo in repos])
    index = rng.integers(0, len(repos), size=(RESAMPLES, len(repos)))
    repo_ci = (100 * np.quantile(sums[index].sum(axis=1) / sizes[index].sum(axis=1), [0.025, 0.975])).tolist()
    return {"task_ci": task_ci, "repository_ci": repo_ci}


def main() -> None:
    with TASKS.open(newline="") as handle:
        meta = list(csv.DictReader(handle))
    if len(meta) != 150 or len({row["task_id"] for row in meta}) != 150:
        raise SystemExit("full-source task table is not 150 unique tasks")
    rows = []
    capsule_mismatch = []
    for item in meta:
        task_id = item["task_id"]
        full = load_arm(FULL, task_id)
        contract = load_arm(CONTRACT, task_id)
        if int(item["functional_pass"]) != full["pass"]:
            raise SystemExit(f"full-source table disagrees with eval for {task_id}")
        if full["capsule"] and contract["capsule"] and full["capsule"] != contract["capsule"]:
            capsule_mismatch.append(task_id)
        if full["pass"] and contract["pass"]:
            pair = "both"
        elif full["pass"]:
            pair = "full_only"
        elif contract["pass"]:
            pair = "contract_only"
        else:
            pair = "neither"
        rows.append(
            {
                "task_id": task_id,
                "repository": item["repository"],
                "lift_type": item["lift_type"],
                "construction_group": item["construction_group"],
                "full_functional_pass": full["pass"],
                "contract_functional_pass": contract["pass"],
                "pair_class": pair,
                "full_first_failure_stage": full["stage"],
                "contract_first_failure_stage": contract["stage"],
                "capsule_match": int(full["capsule"] == contract["capsule"]),
            }
        )
    rows.sort(key=lambda row: row["task_id"])
    out_csv = HERE / "paired_claude_150.csv"
    with out_csv.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    full = np.array([row["full_functional_pass"] for row in rows])
    contract = np.array([row["contract_functional_pass"] for row in rows])
    delta = full - contract
    full_only = int((delta == 1).sum())
    contract_only = int((delta == -1).sum())
    intervals = bootstrap(delta.astype(float), [row["repository"] for row in rows])
    claude = {
        "configuration": "Claude Sonnet 5",
        "n": 150,
        "full_pass": int(full.sum()),
        "contract_pass": int(contract.sum()),
        "both": int(((full == 1) & (contract == 1)).sum()),
        "full_only": full_only,
        "contract_only": contract_only,
        "neither": int(((full == 0) & (contract == 0)).sum()),
        "delta_pp": 100 * float(delta.mean()),
        "paired_bootstrap_95ci_pp": intervals["task_ci"],
        "repository_cluster_bootstrap_95ci_pp": intervals["repository_ci"],
        "mcnemar_exact_p": exact_p(full_only, contract_only),
        "capsule_mismatch": capsule_mismatch,
    }
    family = []
    for published in PUBLISHED:
        family.append(
            {
                "configuration": published["configuration"],
                "full_only": published["full_only"],
                "contract_only": published["contract_only"],
                "mcnemar_exact_p": exact_p(published["full_only"], published["contract_only"]),
            }
        )
    family.append(
        {
            "configuration": claude["configuration"],
            "full_only": full_only,
            "contract_only": contract_only,
            "mcnemar_exact_p": claude["mcnemar_exact_p"],
        }
    )
    holm(family)
    claude["holm_p_four_configurations"] = next(
        row["holm_p"] for row in family if row["configuration"] == "Claude Sonnet 5"
    )
    by_lift = []
    for lift in ("Direct", "Adapted", "Composite"):
        subset = [row for row in rows if row["lift_type"] == lift]
        by_lift.append(
            {
                "lift_type": lift,
                "n": len(subset),
                "full_pass": sum(row["full_functional_pass"] for row in subset),
                "contract_pass": sum(row["contract_functional_pass"] for row in subset),
                "both": sum(row["pair_class"] == "both" for row in subset),
                "full_only": sum(row["pair_class"] == "full_only" for row in subset),
                "contract_only": sum(row["pair_class"] == "contract_only" for row in subset),
                "neither": sum(row["pair_class"] == "neither" for row in subset),
            }
        )
    payload = {
        "seed": SEED,
        "bootstrap_resamples": RESAMPLES,
        "functional_pass": "build and public and hidden and isolation",
        "claude": claude,
        "holm_four_configurations": family,
        "by_lift_type": by_lift,
        "published_three_configuration_holm_unchanged_inputs": {
            "note": "Adding Claude changes the Holm multipliers. Raw McNemar p-values of Luna, Pro, and Qwen are unchanged.",
        },
    }
    (HERE / "paired_claude_150_stats.json").write_text(json.dumps(payload, indent=2) + "\n")
    ci = claude["paired_bootstrap_95ci_pp"]
    lines = [
        "# Claude paired Full Source and Contract Only",
        "",
        f"Full {claude['full_pass']}/150, Contract {claude['contract_pass']}/150.",
        f"both {claude['both']}, full_only {claude['full_only']}, contract_only {claude['contract_only']}, neither {claude['neither']}.",
        f"Delta {claude['delta_pp']:.1f} pp, 95% paired task bootstrap [{ci[0]:.1f}, {ci[1]:.1f}].",
        f"Exact McNemar p {claude['mcnemar_exact_p']:.3e}; Holm across four configurations {claude['holm_p_four_configurations']:.3e}.",
        f"Capsule mismatches: {len(capsule_mismatch)}.",
        "",
        "| Configuration | Only Full | Only Contract | Raw p | Holm p (four tests) |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in family:
        lines.append(
            f"| {row['configuration']} | {row['full_only']} | {row['contract_only']} | "
            f"{row['mcnemar_exact_p']:.3e} | {row['holm_p']:.3e} |"
        )
    (HERE / "paired_claude_150_stats.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
