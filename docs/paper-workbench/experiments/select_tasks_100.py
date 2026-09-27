"""Freeze a prospective 100-task extension of the paired source ablation.

Membership uses only the frozen task inventory and the original deterministic
40-task ranking. The decision to extend was made after the 40-task results.
No model or evaluator outcomes enter task selection.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

from select_tasks import ROOT, HERE, SEED, rank

SIZE = 100
SOURCE_40 = HERE / "source_ablation_40.json"
OUT_JSON = HERE / "source_ablation_100.json"
OUT_TXT = HERE / "source_ablation_100.txt"


def build() -> dict:
    sources = json.loads((ROOT / "docs/paper-workbench/paper_sources.json").read_text())
    inventory = ROOT / sources["inputs"]["task_inventory"]
    population = [row for row in json.loads(inventory.read_text())["tasks"]
                  if row["release_stratum"] == "python150"]
    assert len(population) == len({row["task_id"] for row in population}) == 150
    prior = json.loads(SOURCE_40.read_text())
    assert prior["seed"] == SEED and prior["sample_size"] == 40
    # The original inventory was later reorganized. Verify the actual fixed
    # population/strata and all prior labels rather than equating file hashes.

    strata = defaultdict(list)
    for row in population:
        cohort = "later" if row["construction_group_150"] == "hard50" else "earlier"
        strata[(cohort, row["historical_lift_type"])].append(row)
    assert {(item["cohort"], item["lift_type"]): item["population_n"]
            for item in prior["strata"]} == {key: len(rows) for key, rows in strata.items()}
    prior_labels = {row["task_id"]: (row["cohort"], row["lift_type"], row["source_snapshot_id"])
                    for row in prior["tasks"]}
    assert all(prior_labels[row["task_id"]] == (
        "later" if row["construction_group_150"] == "hard50" else "earlier",
        row["historical_lift_type"], row["source_snapshot_id"])
        for row in population if row["task_id"] in prior_labels)
    quotas = {key: len(rows) * SIZE // len(population) for key, rows in strata.items()}
    remainder_order = sorted(strata, key=lambda key: (
        -(len(strata[key]) * SIZE % len(population)), key))
    for key in remainder_order[:SIZE - sum(quotas.values())]:
        quotas[key] += 1

    selected = [row for key in sorted(strata)
                for row in sorted(strata[key], key=lambda item: rank(item["task_id"]))[:quotas[key]]]
    prior_ids = {row["task_id"] for row in prior["tasks"]}
    selected_ids = {row["task_id"] for row in selected}
    assert len(selected_ids) == SIZE and prior_ids <= selected_ids
    schedule = sorted(selected, key=lambda row: rank(row["task_id"], "schedule"))
    records = []
    for index, row in enumerate(schedule):
        records.append({
            "task_id": row["task_id"],
            "task_path": f"benchmark/tasks/{row['task_id']}",
            "cohort": "later" if row["construction_group_150"] == "hard50" else "earlier",
            "lift_type": row["historical_lift_type"],
            "feature_family": row["historical_feature_family"],
            "source_repo_id": row["source_repo_id"],
            "source_snapshot_id": row["source_snapshot_id"],
            "in_original_40": row["task_id"] in prior_ids,
            "arm_order": ["full_repository", "contract_only"] if index % 2 == 0
                         else ["contract_only", "full_repository"],
        })
    return {
        "schema": "featureliftbench.supplementary_selection_extension.v1",
        "seed": SEED,
        "population": "fixed python150 main-comparison task set",
        "selection": "Original cohort x lift-type strata, proportional largest-remainder quotas, original SHA256 ordering within strata",
        "extension_decided_after_40_task_outcomes": True,
        "model_or_evaluator_outcomes_used_to_select_task_ids": False,
        "membership_only_no_agent_runs": True,
        "inventory_path": str(inventory.relative_to(ROOT)),
        "inventory_sha256": hashlib.sha256(inventory.read_bytes()).hexdigest(),
        "parent_40_inventory_sha256": prior["inventory_sha256"],
        "inventory_identity_note": "Current inventory file differs from the original 40-task inventory; six stratum sizes and all 40 existing task labels/snapshots match the frozen 40-task manifest.",
        "parent_40_path": str(SOURCE_40.relative_to(ROOT)),
        "parent_40_sha256": hashlib.sha256(SOURCE_40.read_bytes()).hexdigest(),
        "sample_size": SIZE,
        "original_task_count": len(prior_ids),
        "additional_task_count": len(selected_ids - prior_ids),
        "repository_count": len({row["source_repo_id"] for row in selected}),
        "strata": [{"cohort": key[0], "lift_type": key[1], "population_n": len(strata[key]),
                    "original_n": sum(row["task_id"] in prior_ids for row in strata[key]),
                    "sample_n": quotas[key],
                    "additional_n": quotas[key] - sum(row["task_id"] in prior_ids for row in strata[key])}
                   for key in sorted(strata)],
        "lift_type_counts": dict(sorted(Counter(row["historical_lift_type"] for row in selected).items())),
        "tasks": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify saved selection without writing")
    args = parser.parse_args()
    result = build()
    outputs = {
        OUT_JSON: json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        OUT_TXT: "\n".join(row["task_id"] for row in result["tasks"]) + "\n",
    }
    for path, content in outputs.items():
        if args.check:
            assert path.read_text() == content, f"Selection differs: {path}"
        else:
            if path.exists() and path.read_text() != content:
                raise SystemExit(f"Refusing to replace a different saved selection: {path}")
            path.write_text(content)
    print(json.dumps({key: result[key] for key in ["sample_size", "original_task_count",
          "additional_task_count", "repository_count", "lift_type_counts", "strata"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
