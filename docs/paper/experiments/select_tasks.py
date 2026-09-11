"""Select an outcome-blind supplementary sample; no model or evaluator calls."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SEED = "featureliftbench-source-ablation-20260911"


def rank(task_id: str, purpose: str = "selection") -> str:
    return hashlib.sha256(f"{SEED}|{purpose}|{task_id}".encode()).hexdigest()


def build() -> dict:
    sources = json.loads((ROOT / "docs/paper/paper_sources.json").read_text(encoding="utf-8"))
    inventory = ROOT / sources["inputs"]["task_inventory"]
    rows = json.loads(inventory.read_text(encoding="utf-8"))["tasks"]
    common = [r for r in rows if r["release_stratum"] == "python150"]
    assert len(common) == len({r["task_id"] for r in common}) == 150
    strata = defaultdict(list)
    for r in common:
        cohort = "later" if r["construction_group_150"] == "hard50" else "earlier"
        strata[(cohort, r["historical_lift_type"])].append(r)
    quotas = {k: len(v) * 40 // 150 for k, v in strata.items()}
    remainder_order = sorted(strata, key=lambda k: (-(len(strata[k]) * 40 % 150), k))
    for k in remainder_order[:40 - sum(quotas.values())]:
        quotas[k] += 1
    selected = []
    for k in sorted(strata):
        selected.extend(sorted(strata[k], key=lambda r: rank(r["task_id"]))[:quotas[k]])
    ids = {r["task_id"] for r in selected}
    assert len(ids) == 40
    smoke = []
    for lift in ("Direct", "Adapted", "Composite"):
        candidates = [r for r in common if r["task_id"] not in ids and r["historical_lift_type"] == lift]
        smoke.append(min(candidates, key=lambda r: rank(r["task_id"], "smoke"))["task_id"])
    schedule = sorted(selected, key=lambda r: rank(r["task_id"], "schedule"))
    records = []
    for i, r in enumerate(schedule):
        records.append({
            "task_id": r["task_id"],
            "task_path": f"benchmark/tasks/{r['task_id']}",
            "cohort": "later" if r["construction_group_150"] == "hard50" else "earlier",
            "lift_type": r["historical_lift_type"],
            "feature_family": r["historical_feature_family"],
            "source_repo_id": r["source_repo_id"],
            "source_snapshot_id": r["source_snapshot_id"],
            "arm_order": ["full_repository", "contract_only"] if i % 2 == 0 else ["contract_only", "full_repository"],
        })
    return {
        "schema": "featureliftbench.supplementary_selection.v1",
        "seed": SEED,
        "population": "common 150-task comparison; benchmark remains 200 tasks",
        "selection": "proportional cohort x lift-type strata; largest remainder; SHA256 ordering within strata",
        "outcomes_used_for_selection": False,
        "inventory_path": str(inventory.relative_to(ROOT)).replace("\\", "/"),
        "inventory_sha256": hashlib.sha256(inventory.read_bytes()).hexdigest(),
        "sample_size": 40,
        "repository_count": len({r["source_repo_id"] for r in selected}),
        "strata": [{"cohort": k[0], "lift_type": k[1], "population_n": len(strata[k]), "sample_n": quotas[k]} for k in sorted(strata)],
        "family_counts": dict(sorted(Counter(r["historical_feature_family"] for r in selected).items())),
        "smoke_task_ids": smoke,
        "tasks": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify the saved selection without writing")
    args = parser.parse_args()
    result = build()
    outputs = {
        HERE / "source_ablation_40.json": json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        HERE / "source_ablation_40.txt": "\n".join(r["task_id"] for r in result["tasks"]) + "\n",
        HERE / "source_ablation_smoke_3.txt": "\n".join(result["smoke_task_ids"]) + "\n",
    }
    for path, content in outputs.items():
        if args.check:
            assert path.read_text(encoding="utf-8") == content, f"Selection differs: {path}"
        else:
            if path.exists() and path.read_text(encoding="utf-8") != content:
                raise SystemExit(f"Refusing to replace a different saved selection: {path}")
            path.write_bytes(content.encode("utf-8"))
    print(json.dumps({"sample": 40, "repositories": result["repository_count"], "strata": result["strata"], "smoke": result["smoke_task_ids"], "experiments_run": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
