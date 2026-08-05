#!/usr/bin/env python3
"""Join behavior, closure, taxonomy, subset, and quarantine state into one review queue."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TASKS = ROOT / "benchmark/tasks"
SUBSET_PATH = ROOT / "artifacts/research_analysis/v1_1/diagnostic_subset_manifest.json"
TAXONOMY_PATH = ROOT / "artifacts/research_analysis/python150_task_taxonomy.csv"
QUARANTINE_PATH = ROOT / "experiments/validation/v1_1/v1_1_oracle_validation/536c2beec549fdc8/quarantine_manifest.json"
OUTPUT = ROOT / "artifacts/research_analysis/v1_1/review_queue.csv"


FIELDS = [
    "task_id", "diagnostic_subset", "challenge_group", "pilot_task", "contract_suspect",
    "behavior_review_status", "public_unmapped_count", "hidden_unmapped_count",
    "closure_review_status", "file_gold_completeness", "taxonomy_review_status",
    "quarantine_status", "quarantine_root_cause", "priority", "required_actions",
]


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def main() -> int:
    subset = load(SUBSET_PATH)
    representative = set(subset["representative_20"])
    challenge = set(subset["challenge_20"])
    groups = {
        task_id: group
        for group, task_ids in subset["challenge_groups"].items()
        for task_id in task_ids
    }
    pilot = set(subset["challenge_groups"]["pilot_10"])
    suspects = set(subset["challenge_groups"]["contract_review_6"])
    taxonomy = {}
    with TAXONOMY_PATH.open(encoding="utf-8", newline="") as handle:
        taxonomy = {row["task_id"]: row for row in csv.DictReader(handle)}
    quarantine = {
        item["task_id"]: item
        for item in load(QUARANTINE_PATH).get("tasks") or []
        if isinstance(item, dict)
    }
    rows = []
    for task_dir in sorted(path for path in TASKS.iterdir() if (path / "metadata.json").is_file()):
        task_id = task_dir.name
        behavior = load(task_dir / "evaluation/behavior_contract.json")
        closure_path = task_dir / "evaluation/closure_gold.json"
        closure = load(closure_path) if closure_path.is_file() else {}
        q = quarantine.get(task_id, {})
        actions = []
        if q:
            actions.append("repair_or_adjudicate_quarantined_task")
        if behavior.get("review_status") not in {"author_reviewed", "double_reviewed", "adjudicated"}:
            actions.append("review_behavior_mapping")
        if task_id in representative | challenge and (
            (closure.get("gold_completeness") or {}).get("file") != "complete"
            or (closure.get("review") or {}).get("status") != "adjudicated"
        ):
            actions.append("double_review_and_adjudicate_closure")
        if taxonomy[task_id].get("review_status") == "needs_review":
            actions.append("adjudicate_taxonomy")
        if task_id in suspects:
            actions.append("adjudicate_contract_suspect")
        if q or task_id in pilot or task_id in suspects:
            priority = "P0"
        elif task_id in representative or task_id in challenge:
            priority = "P1"
        elif actions:
            priority = "P2"
        else:
            priority = "done"
        rows.append({
            "task_id": task_id,
            "diagnostic_subset": "representative20" if task_id in representative else ("challenge20" if task_id in challenge else ""),
            "challenge_group": groups.get(task_id, ""),
            "pilot_task": str(task_id in pilot).lower(),
            "contract_suspect": str(task_id in suspects).lower(),
            "behavior_review_status": behavior.get("review_status", "missing"),
            "public_unmapped_count": len(behavior.get("unmapped_public_test_nodeids") or []),
            "hidden_unmapped_count": len(behavior.get("unmapped_hidden_test_nodeids") or []),
            "closure_review_status": (closure.get("review") or {}).get("status", "missing"),
            "file_gold_completeness": (closure.get("gold_completeness") or {}).get("file", "NA"),
            "taxonomy_review_status": taxonomy[task_id].get("review_status", "missing"),
            "quarantine_status": "quarantined" if q else "active",
            "quarantine_root_cause": q.get("root_cause_subtype", ""),
            "priority": priority,
            "required_actions": ";".join(actions),
        })
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    counts = {priority: sum(row["priority"] == priority for row in rows) for priority in ("P0", "P1", "P2", "done")}
    print(f"wrote {OUTPUT.relative_to(ROOT)}: rows={len(rows)} priorities={counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
