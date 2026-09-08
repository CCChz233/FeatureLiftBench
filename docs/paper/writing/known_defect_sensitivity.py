"""Post hoc known-defect exclusion, using existing results only.

Run from any directory with Python 3:
    python docs/paper/writing/known_defect_sensitivity.py

This is a non-exhaustive sensitivity view, not a new official leaderboard.
The seven task IDs were flagged by assistant-first-pass failure review. No
benchmark definitions, labels, submissions, or evaluation results are modified.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "reports/paper_analysis/python150_prime_v2_analysis_20260905"
RESULTS = SOURCE / "task_results.csv"
ANNOTATIONS = SOURCE / "failure_root_cause_annotations.csv"
OUTPUT = Path(__file__).with_suffix(".json")
FREEZE = "6c20ff0307762503a73cbb9ff32e9992c6446e4b17483a68373027be58cbf419"
PREDECESSOR_FREEZE = "0b106842710368a497b49b7f6714e0dfea54778d1fb2dae38c93ea449b339542"
MODELS = [
    "deepseek-v4-pro", "deepseek-v4-flash", "gpt-5.6-luna",
    "glm-5.3-flash", "qwen3.6-35b-a3b-fp8", "gpt-oss-120b",
]
EXCLUDED_IDS = {
    "click__lazy_command_core__hard3_001",
    "flake8__plugin_options_core__hard3_001",
    "hatch__project_metadata_core__hard3_001",
    "pluggy__hook_wrapper_core__hard3_001",
    "pytest__ini_markers_core__001",
    "readme_renderer__content_type_core__hard3_001",
    "setuptools_scm__version_normalize_core__hard3_001",
}
GATE_FIELDS = {
    "build_pass": "build_pass", "public_pass": "public_tests_pass",
    "hidden_pass": "hidden_tests_pass", "isolation_pass": "isolation_pass",
}


def boolean(value: str) -> bool:
    assert value.lower() in {"true", "false"}, value
    return value.lower() == "true"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def summarise(rows: list[dict[str, str]]) -> dict:
    passed = sum(boolean(row["functional_pass"]) for row in rows)
    return {
        "n": len(rows), "pass": passed, "fail": len(rows) - passed,
        "pass_rate": passed / len(rows),
        "empty": sum(not boolean(row["usable_submission"]) for row in rows),
    }


def main() -> None:
    rows = read_csv(RESULTS)
    annotations = read_csv(ANNOTATIONS)
    keys = [(row["task_id"], row["model"]) for row in rows]
    assert len(rows) == 900 and len(set(keys)) == 900
    assert set(row["model"] for row in rows) == set(MODELS)
    freeze_counts = Counter(row["freeze_id"] for row in rows)
    assert freeze_counts == {FREEZE: 522, PREDECESSOR_FREEZE: 378}
    assert {row["eval_docker_image"] for row in rows} == {"featureliftbench-eval:python200-prime-212930ea"}
    defects = [row for row in annotations if row["root_cause_primary"] == "task_or_evaluator_defect"]
    assert len(defects) == 14
    assert {row["task_id"] for row in defects} == EXCLUDED_IDS
    assert {row["evidence_eligibility"] for row in defects} == {"benchmark_invalid_candidate"}
    assert {row["review_status"] for row in defects} == {"assistant_first_pass"}
    by_task: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_model: dict[str, list[dict[str, str]]] = defaultdict(list)
    raw_checked = 0
    raw_missing = 0
    for row in rows:
        by_task[row["task_id"]].append(row)
        by_model[row["model"]].append(row)
        gate_pass = all(boolean(row[field]) for field in GATE_FIELDS) if boolean(row["usable_submission"]) else False
        assert boolean(row["functional_pass"]) == (boolean(row["usable_submission"]) and gate_pass)
        suite = "python150-prime-v2-main-r1" if row["model"] == MODELS[0] else "python200-prime-v2-main-r1"
        raw_path = ROOT / "experiments/python/openhands" / row["model"] / suite / row["task_id"] / "eval/result.json"
        assert raw_path.is_file() == boolean(row["has_result_json"]), str(raw_path)
        if not raw_path.is_file():
            raw_missing += 1
            assert not boolean(row["functional_pass"])
            continue
        raw = json.loads(raw_path.read_text(encoding="utf-8"))
        for csv_key, raw_key in GATE_FIELDS.items():
            assert boolean(row[csv_key]) == bool(raw.get(raw_key, False)), (row["model"], row["task_id"], csv_key)
        if boolean(row["functional_pass"]):
            compact = raw.get("compactness", {})
            for csv_key, raw_key in (("copied_fraction", "copied_fraction"), ("rres", "extraction_ratio_to_reference")):
                assert abs(float(row[csv_key]) - float(compact[raw_key])) < 1e-6
        raw_checked += 1
    assert len(by_task) == 150 and set(EXCLUDED_IDS) <= set(by_task)
    for task_rows in by_task.values():
        assert len(task_rows) == 6
        assert {row["model"] for row in task_rows} == set(MODELS)
        assert len({row["hard3"] for row in task_rows}) == 1
        assert len({row["lift_type"] for row in task_rows}) == 1
    model_summary = []
    for model in MODELS:
        full = by_model[model]
        kept = [row for row in full if row["task_id"] not in EXCLUDED_IDS]
        removed = [row for row in full if row["task_id"] in EXCLUDED_IDS]
        assert len(full) == 150 and len(kept) == 143 and len(removed) == 7
        model_summary.append({"model": model, "frozen_150": summarise(full), "excluded_7": summarise(removed), "post_hoc_143": summarise(kept)})
    unsolved = sorted(task for task, task_rows in by_task.items() if not any(boolean(row["functional_pass"]) for row in task_rows))
    remaining_unsolved = [task for task in unsolved if task not in EXCLUDED_IDS]
    excluded_details = []
    for task in sorted(EXCLUDED_IDS):
        task_rows = {row["model"]: row for row in by_task[task]}
        excluded_details.append({
            "task_id": task, "hard3": boolean(task_rows[MODELS[0]]["hard3"]),
            "functional_pass_by_model": {model: boolean(task_rows[model]["functional_pass"]) for model in MODELS},
            "first_failure_stage_by_model": {model: task_rows[model]["first_failure_stage"] for model in MODELS},
            "flag_reason": next(row["validity_reason"] for row in defects if row["task_id"] == task),
        })
    delivered = [row for row in rows if boolean(row["usable_submission"])]
    payload = {
        "analysis_status": "post_hoc_non_exhaustive_known_defect_exclusion_not_official_leaderboard",
        "interpretation": "The excluded IDs were selected from observed failures by assistant-first-pass review; this view does not certify all remaining tasks, correct frozen outcomes, or measure performance on a newly validated benchmark.",
        "metric": "Functional Pass = usable submission and Build and Public and Hidden and Isolation; empty submissions remain failures.",
        "campaign_freeze_id": FREEZE,
        "observed_run_freeze_counts": dict(freeze_counts),
        "freeze_caveat": "The existing merged campaign retains 126 predecessor-freeze records for each of Flash, Luna, and Qwen, alongside 24 v2 records each; Pro, GLM, and OSS have 150 v2 records each. All CSV records report evaluator image python200-prime-212930ea. This script verifies counts and raw gates, not equivalence of predecessor and v2 task contracts.",
        "sources": [{"path": str(path.relative_to(ROOT)).replace('\\', '/'), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in (RESULTS, ANNOTATIONS)],
        "qa": {"rows": len(rows), "unique_task_model_keys": len(set(keys)), "tasks": len(by_task), "models": len(MODELS), "raw_result_files_checked": raw_checked, "raw_result_files_absent": raw_missing, "gate_mismatches": 0, "passing_compactness_mismatches": 0, "defect_annotation_rows": len(defects), "checks": "Assertions enforce key uniqueness, complete 150 x 6 matrix, recorded campaign freeze composition and evaluator image, exact seven known IDs, gate agreement with existing raw JSON, and pass-conditioned compactness agreement."},
        "by_model": model_summary,
        "excluded_tasks": excluded_details,
        "unsolved_by_all_six": {
            "frozen_150": {"n": len(unsolved), "hard3": sum(boolean(by_task[task][0]["hard3"]) for task in unsolved)},
            "post_hoc_143": {"n": len(remaining_unsolved), "hard3": sum(boolean(by_task[task][0]["hard3"]) for task in remaining_unsolved)},
            "remaining_task_ids": remaining_unsolved,
        },
        "frozen_gate_audit": {
            "delivered_artifacts": len(delivered),
            "independent_failures": {field: sum(not boolean(row[field]) for row in delivered) for field in GATE_FIELDS},
            "isolation_only_after_other_gates": sum(boolean(row["build_pass"]) and boolean(row["public_pass"]) and boolean(row["hidden_pass"]) and not boolean(row["isolation_pass"]) for row in delivered),
            "first_failure_counts": dict(Counter(row["first_failure_stage"] for row in rows)),
        },
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), "qa": payload["qa"], "by_model": model_summary, "unsolved_counts": {k: v for k, v in payload["unsolved_by_all_six"].items() if k != "remaining_task_ids"}}, indent=2))


if __name__ == "__main__":
    main()
