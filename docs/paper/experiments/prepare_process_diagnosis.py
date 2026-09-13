"""Prepare private inputs for source-exposure diagnosis; no model calls or evals.

This inventories annotations and saved run locations. It does not infer that
an entrypoint exists, that an action succeeded, or that a model read a file.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "docs/paper"))
from paper_inputs import input_path, MANIFEST


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "reports/paper_analysis/source_exposure/preflight")
    args = parser.parse_args()
    membership = input_path("task_selection")
    ids = read(membership)["task_ids"]
    sample = ROOT / "docs/paper/experiments/source_ablation_40.txt"
    sample_ids = [x.strip() for x in sample.read_text().splitlines() if x.strip()]
    assert len(ids) == len(set(ids)) == 150
    assert len(sample_ids) == len(set(sample_ids)) == 40 and set(sample_ids) <= set(ids)
    tasks = []
    for tid in ids:
        folder = ROOT / "benchmark/tasks" / tid
        meta = read(folder / "metadata.json")
        candidates = [meta.get(k, {}).get("source_entrypoints", [])
                      for k in ("evaluation_spec", "public_spec", "feature")]
        candidates.append(meta.get("source_hints", []))
        entries = next(([x for x in c if isinstance(x, str) and x.strip()]
                        for c in candidates if isinstance(c, list) and c), [])
        oracle = folder / "evaluation/oracle_manifest.json"
        closure = folder / "evaluation/closure_gold.json"
        required = read(oracle).get("required_source_files", []) if oracle.exists() else []
        tasks.append({"task_id": tid, "in_hint_sample": tid in sample_ids,
                      "entrypoints_declared": entries,
                      "entrypoint_mapping_status": "requires_file_and_symbol_verification",
                      "required_source_files": required,
                      "closure_gold_path": closure.relative_to(ROOT).as_posix() if closure.exists() else None,
                      "closure_annotation_scope": read(closure).get("annotation_scope") if closure.exists() else None,
                      "metadata_sha256": digest(folder / "metadata.json"),
                      "oracle_manifest_sha256": digest(oracle) if oracle.exists() else None,
                      "closure_gold_sha256": digest(closure) if closure.exists() else None})
    with input_path("main_results").open(encoding="utf-8-sig", newline="") as handle:
        results = [r for r in csv.DictReader(handle) if r["task_id"] in ids]
    models = {m["id"]: m for m in MANIFEST["models"]}
    assert len(results) == len({(r["model"], r["task_id"]) for r in results}) == 900
    index = []
    for row in results:
        run = ROOT / models[row["model"]]["run_directory"] / row["task_id"]
        events = run / "agent/openhands_events.jsonl"
        index.append({"model": row["model"], "task_id": row["task_id"],
                      "functional_pass": row["functional_pass"],
                      "first_failure_stage": row["first_failure_stage"],
                      "run_directory": run.relative_to(ROOT).as_posix(),
                      "run_json_exists": (run / "run.json").is_file(),
                      "events_path": events.relative_to(ROOT).as_posix(),
                      "events_present_nonempty": events.is_file() and events.stat().st_size > 0})
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / "targets.private.json").write_text(json.dumps({"tasks": tasks}, indent=2) + "\n", encoding="utf-8")
    with (out / "run_index.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(index[0]))
        writer.writeheader(); writer.writerows(index)
    summary = {"task_count": len(tasks), "hint_sample_count": len(sample_ids),
               "tasks_with_declared_entrypoints": sum(bool(t["entrypoints_declared"]) for t in tasks),
               "tasks_with_required_source_files": sum(bool(t["required_source_files"]) for t in tasks),
               "tasks_with_closure_gold": sum(bool(t["closure_gold_path"]) for t in tasks),
               "run_cells": len(index),
               "nonempty_event_files": sum(r["events_present_nonempty"] for r in index),
               "outcome_inventory": dict(Counter(r["first_failure_stage"] for r in index)),
               "membership_sha256": digest(membership), "sample_sha256": digest(sample),
               "main_results_sha256": digest(input_path("main_results")),
               "note": "Inventory only. File availability is not a complete or valid trace; annotations require scope and path checks. Never mount targets.private.json in an agent container."}
    (out / "preflight.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
