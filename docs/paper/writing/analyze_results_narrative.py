"""Recompute descriptive evidence for the results-writing memo; no experiments."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "docs/paper"


def main():
    spec = json.loads((PAPER / "paper_sources.json").read_text(encoding="utf-8"))
    source = ROOT / spec["inputs"]["main_results"]
    with source.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    truth = lambda row, key: row[key].lower() == "true"
    assert len(rows) == 900
    assert len({(r["model"], r["task_id"]) for r in rows}) == 900
    success_sets, task_sets, summaries = {}, [], []
    for model in spec["models"]:
        group = [r for r in rows if r["model"] == model["id"]]
        assert len(group) == 150
        task_sets.append({r["task_id"] for r in group})
        passed = {r["task_id"] for r in group if truth(r, "functional_pass")}
        assert len(passed) == model["main_passes"]
        success_sets[model["short"]] = passed
        delivered = [r for r in group if truth(r, "usable_submission")]
        prefix = [r for r in delivered if truth(r, "build_pass") and truth(r, "public_pass")]
        hidden_failures = sum(not truth(r, "hidden_pass") for r in prefix)
        first = Counter(r["first_failure_stage"] for r in group)
        assert hidden_failures == first["hidden_failure"]
        summaries.append({
            "model": model["display"], "assigned": 150, "passed": len(passed),
            "delivered": len(delivered), "first_outcomes": dict(first),
            "pass_given_delivery_pct": 100 * len(passed) / len(delivered),
            "build_and_public_passed": len(prefix),
            "hidden_fail_after_build_public": hidden_failures,
            "hidden_fail_given_build_public_pct": 100 * hidden_failures / len(prefix),
        })
    assert all(tasks == task_sets[0] for tasks in task_sets)
    union = set.union(*success_sets.values())
    pro_fail = task_sets[0] - success_sets["Pro"]
    all_fail = task_sets[0] - union
    frequency = Counter(sum(task in s for s in success_sets.values()) for task in task_sets[0])
    assert [frequency[k] for k in range(7)] == [28, 7, 9, 22, 36, 31, 17]
    output = {
        "source": spec["inputs"]["main_results"],
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "scope": "Six configurations, identical 150 tasks, 900 retained outcomes; descriptive reanalysis only.",
        "configurations": summaries,
        "solve_frequency": dict(sorted(frequency.items())),
        "union_successes": len(union), "union_success_rate_pct": 100 * len(union) / 150,
        "union_extra_over_pro": len(union - success_sets["Pro"]),
        "top_three_union": len(success_sets["Pro"] | success_sets["Flash"] | success_sets["Luna"]),
        "all_fail": len(all_fail), "pro_fail": len(pro_fail),
        "all_fail_share_of_pro_fail_pct": 100 * len(all_fail) / len(pro_fail),
        "interpretation_limits": [
            "The union is retrospective coverage, not an implemented selection or ensemble system.",
            "Conditional rates use model-specific selected artifacts; they are not counterfactual improvements or adjusted rankings.",
            "Both Public and Hidden benchmark tests are withheld; differences do not demonstrate public-test overfitting.",
            "Failure gates locate outcomes, not semantic root causes; all-fail is not intrinsic unsolvability.",
            "Source-ablation hypothetical values are excluded.",
        ],
    }
    target = PAPER / "writing/results_narrative_evidence.json"
    target.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(target), "rows": len(rows), "union": len(union), "all_fail": len(all_fail)}))


if __name__ == "__main__":
    main()
