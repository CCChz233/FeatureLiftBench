#!/usr/bin/env python3
"""Build a portable registry and study summaries for local experiment assets."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "harness"))

from featureliftbench.suite_utils import resolve_suite_artifact_path

EXPERIMENTS_ROOT = REPO_ROOT / "experiments"
DEFAULT_OUTPUT = EXPERIMENTS_ROOT / "registry"

FROZEN_RUN_IDS = {
    "main-flash-20260705-232429",
    "qwen36-27b-fp8-main-20260704-001328",
    "qwen36-35b-a3b-fp8-main-20260704-001313",
    "main-20260702-212731",
    "batch3-flash-20260707-113104",
    "batch3-flash-20260707-wave2wave4",
    "batch3-flash-20260708-wave5",
}
SUPERSEDED_RUN_IDS = {"batch3-flash-20260707-112646"}

PYTHON150_COMPONENTS = {
    "deepseek-v4-flash": {
        "status": "frozen",
        "runs": [
            "main-flash-20260705-232429",
            "batch3-flash-20260707-113104",
            "batch3-flash-20260707-wave2wave4",
            "batch3-flash-20260708-wave5",
        ],
    },
    "qwen3.6-27b-fp8": {
        "status": "candidate",
        "runs": [
            "qwen36-27b-fp8-main-20260704-001328",
            "hard50-qwen3.6-27b-fp8-20260720-023500",
        ],
    },
    "qwen3.6-35b-a3b-fp8": {
        "status": "candidate",
        "runs": [
            "qwen36-35b-a3b-fp8-main-20260704-001313",
            "hard50-qwen3.6-35b-a3b-fp8-20260720-022800",
        ],
    },
    "qwen3-coder-30b-a3b-instruct": {
        "status": "incomplete",
        "runs": ["main-20260702-212731"],
    },
}


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def relative(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()


def task_set_hash(task_ids: list[str]) -> str:
    content = "".join(f"{task_id}\n" for task_id in sorted(task_ids))
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _scope(path: Path, task_count: int) -> str:
    parts = set(path.parts)
    name = path.name.lower()
    if "GO" in parts:
        return "go-calibration"
    if "smoke" in parts:
        return "smoke"
    if "v1_1_infra_reevaluation" in parts:
        return "infra-reevaluation"
    if task_count == 100 and ("main" in name or "core" in name):
        return "core100"
    if task_count == 50 and ("hard50" in name or "batch3" in name):
        return "hard50"
    if "batch3" in name:
        return "hard50-fragment"
    return "other"


def _category(path: Path) -> str:
    parts = set(path.parts)
    if "python" in parts and "openhands" in parts:
        return "leaderboard"
    if "GO" in parts:
        return "calibration"
    if "smoke" in parts:
        return "smoke"
    if any(part.startswith("v1_1_") for part in path.parts):
        return "validation"
    return "support"


def _lifecycle(path: Path, run_id: str) -> str:
    if _category(path) != "leaderboard":
        return "support"
    if run_id in SUPERSEDED_RUN_IDS:
        return "superseded"
    if run_id in FROZEN_RUN_IDS:
        return "frozen"
    return "candidate"


def _read_task_row(suite_dir: Path, entry: dict[str, Any]) -> dict[str, Any]:
    task_id = str(entry.get("task_id") or "")
    run_path = resolve_suite_artifact_path(
        suite_dir, task_id, "run.json", entry.get("run_json")
    )
    run = load_json(run_path) if run_path.is_file() else {}
    evaluation = run.get("evaluation") if isinstance(run.get("evaluation"), dict) else {}
    eval_path = resolve_suite_artifact_path(
        suite_dir,
        task_id,
        "eval/result.json",
        evaluation.get("result_json") or entry.get("result_json"),
    )
    eval_result = load_json(eval_path) if eval_path.is_file() else {}
    scores = (
        eval_result.get("scores")
        if isinstance(eval_result.get("scores"), dict)
        else evaluation.get("scores")
        if isinstance(evaluation.get("scores"), dict)
        else {}
    )
    agent = run.get("agent") if isinstance(run.get("agent"), dict) else {}
    usage = agent.get("usage") if isinstance(agent.get("usage"), dict) else {}
    # run.status is the composite outcome: an agent failure still fails the
    # task even when an extracted submission passes evaluator tests.
    status = str(run.get("status") or entry.get("status") or "unknown")
    return {
        "task_id": task_id,
        "status": status,
        "final_score": float(scores.get("final_score") or entry.get("final_score") or 0.0),
        "evaluated": eval_path.is_file(),
        "run_json": relative(run_path) if run_path.is_file() else "",
        "result_json": relative(eval_path) if eval_path.is_file() else "",
        "total_tokens": usage.get("total_tokens") or (entry.get("agent_usage") or {}).get("total_tokens"),
        "model": usage.get("model"),
    }


def inspect_suite(suite_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    suite_dir = suite_path.parent
    suite = load_json(suite_path)
    entries = [entry for entry in suite.get("runs", []) if isinstance(entry, dict)]
    rows = [_read_task_row(suite_dir, entry) for entry in entries]
    task_ids = [row["task_id"] for row in rows if row["task_id"]]
    passed = sum(row["status"] == "passed" for row in rows)
    missing = sum(row["status"] == "missing_submission" for row in rows)
    evaluated = sum(bool(row["evaluated"]) for row in rows)
    score_sum = sum(float(row["final_score"]) for row in rows)
    average = score_sum / len(rows) if rows else 0.0
    tokens = sum(
        int(row["total_tokens"])
        for row in rows
        if isinstance(row.get("total_tokens"), (int, float))
    )

    summary = suite.get("summary") if isinstance(suite.get("summary"), dict) else {}
    summary_average = float(summary.get("average_final_score") or 0.0)
    absolute_run_paths = sum(
        isinstance(entry.get("run_json"), str) and Path(entry["run_json"]).is_absolute()
        for entry in entries
    )
    absolute_result_paths = sum(
        isinstance(entry.get("result_json"), str) and Path(entry["result_json"]).is_absolute()
        for entry in entries
    )
    quality_flags: list[str] = []
    if summary.get("total") != len(rows):
        quality_flags.append("summary_total_mismatch")
    if summary.get("passed") != passed:
        quality_flags.append("summary_passed_mismatch")
    if abs(summary_average - average) > 0.000001:
        quality_flags.append("summary_average_mismatch")
    if absolute_run_paths or absolute_result_paths:
        quality_flags.append("absolute_artifact_paths")
    if evaluated < len(rows) - missing:
        quality_flags.append("missing_eval_results")

    agent_config = suite.get("agent_config") if isinstance(suite.get("agent_config"), dict) else {}
    model = agent_config.get("model")
    if not model:
        model = next((row.get("model") for row in rows if row.get("model")), None)
    run_id = suite_dir.name
    raw_path = relative(suite_dir)
    record = {
        "schema_version": "featureliftbench.experiment_run.v1",
        "record_id": raw_path,
        "run_id": run_id,
        "status": _lifecycle(suite_dir, run_id),
        "category": _category(suite_dir),
        "scope": _scope(suite_dir, len(rows)),
        "language": "go" if "GO" in suite_dir.parts else "python",
        "agent": suite.get("agent"),
        "model": model,
        "profile": agent_config.get("profile"),
        "raw_path": raw_path,
        "generated_at": suite.get("generated_at"),
        "task_count": len(rows),
        "task_set_hash": task_set_hash(task_ids),
        "evaluated": evaluated,
        "passed": passed,
        "missing_submission": missing,
        "average_final_score": round(average, 6),
        "total_tokens": tokens,
        "quality": {
            "ok": not quality_flags,
            "flags": quality_flags,
            "summary_average_final_score": round(summary_average, 6),
            "absolute_run_paths": absolute_run_paths,
            "absolute_result_paths": absolute_result_paths,
        },
    }
    return record, rows


def build_study(
    records: list[dict[str, Any]], rows_by_record: dict[str, list[dict[str, Any]]]
) -> dict[str, Any]:
    by_id = {
        record["run_id"]: record
        for record in records
        if record["category"] == "leaderboard"
    }
    models: list[dict[str, Any]] = []
    for model_slug, config in PYTHON150_COMPONENTS.items():
        run_ids = config["runs"]
        missing_runs = [run_id for run_id in run_ids if run_id not in by_id]
        seen: set[str] = set()
        duplicate_tasks: set[str] = set()
        passed = 0
        score_sum = 0.0
        components = []
        for run_id in run_ids:
            record = by_id.get(run_id)
            if record is None:
                continue
            rows = rows_by_record[record["record_id"]]
            task_ids = {row["task_id"] for row in rows}
            duplicate_tasks.update(seen & task_ids)
            seen.update(task_ids)
            passed += sum(row["status"] == "passed" for row in rows)
            score_sum += sum(float(row["final_score"]) for row in rows)
            components.append(
                {
                    "run_id": run_id,
                    "scope": record["scope"],
                    "tasks": len(rows),
                    "passed": record["passed"],
                    "raw_path": record["raw_path"],
                }
            )
        complete = len(seen) == 150 and not duplicate_tasks and not missing_runs
        models.append(
            {
                "model_slug": model_slug,
                "status": config["status"],
                "complete": complete,
                "tasks": len(seen),
                "passed": passed,
                "pass_rate": round(passed / len(seen), 6) if seen else 0.0,
                "average_final_score": round(score_sum / len(seen), 6) if seen else 0.0,
                "task_set_hash": task_set_hash(sorted(seen)),
                "duplicate_tasks": sorted(duplicate_tasks),
                "missing_runs": missing_runs,
                "components": components,
            }
        )
    return {
        "schema_version": "featureliftbench.experiment_study.v1",
        "study_id": "python150-current",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "models": models,
    }


def render_inventory(records: list[dict[str, Any]], study: dict[str, Any]) -> str:
    lines = [
        "# Experiment Inventory",
        "",
        "Generated from task-local `run.json` and `eval/result.json`; `suite.summary` is not trusted as a primary metric source.",
        "",
        "## Python-150 composition",
        "",
        "| Model | Status | Coverage | Pass | Pass rate | Avg final |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for model in study["models"]:
        lines.append(
            f"| `{model['model_slug']}` | {model['status']} | {model['tasks']}/150 | "
            f"{model['passed']}/{model['tasks']} | {model['pass_rate']:.1%} | "
            f"{model['average_final_score']:.6f} |"
        )
    lines.extend(
        [
            "",
            "## Registered suites",
            "",
            "| Run ID | Lifecycle | Category | Scope | Tasks | Evaluated | Pass | Avg final | Quality |",
            "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for record in records:
        quality = "ok" if record["quality"]["ok"] else ", ".join(record["quality"]["flags"])
        lines.append(
            f"| `{record['run_id']}` | {record['status']} | {record['category']} | {record['scope']} | "
            f"{record['task_count']} | {record['evaluated']} | {record['passed']} | "
            f"{record['average_final_score']:.6f} | {quality} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiments-root", type=Path, default=EXPERIMENTS_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    root = args.experiments_root.resolve()
    output = args.output.resolve()
    suite_paths = sorted(
        path
        for path in root.rglob("suite.json")
        if not set(path.relative_to(root).parts) & {"registry", "composites", "bundles"}
    )
    records: list[dict[str, Any]] = []
    rows_by_record: dict[str, list[dict[str, Any]]] = {}
    for suite_path in suite_paths:
        record, rows = inspect_suite(suite_path)
        records.append(record)
        rows_by_record[record["record_id"]] = rows
    records.sort(key=lambda record: (record["category"], record["raw_path"]))
    study = build_study(records, rows_by_record)

    output.mkdir(parents=True, exist_ok=True)
    (output / "studies").mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(UTC).replace(microsecond=0).isoformat()
    inventory = {
        "schema_version": "featureliftbench.experiment_inventory.v1",
        "generated_at": generated_at,
        "suite_count": len(records),
        "runs": records,
    }
    quality = {
        "schema_version": "featureliftbench.experiment_data_quality.v1",
        "generated_at": generated_at,
        "suite_count": len(records),
        "clean_suites": sum(record["quality"]["ok"] for record in records),
        "flagged_suites": [
            {
                "run_id": record["run_id"],
                "raw_path": record["raw_path"],
                **record["quality"],
            }
            for record in records
            if not record["quality"]["ok"]
        ],
    }
    (output / "inventory.json").write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output / "runs.jsonl").write_text(
        "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )
    (output / "data_quality.json").write_text(
        json.dumps(quality, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output / "studies" / "python150-current.json").write_text(
        json.dumps(study, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output / "INVENTORY.md").write_text(render_inventory(records, study), encoding="utf-8")
    print(
        f"registered {len(records)} suites; "
        f"clean={quality['clean_suites']} flagged={len(quality['flagged_suites'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
