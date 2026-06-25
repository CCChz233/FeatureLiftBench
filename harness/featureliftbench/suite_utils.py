"""Shared helpers for suite runs, re-evaluation, and analysis."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EVAL_FLAKE_PYTEST_MISSING = "No module named pytest"
EVAL_TOOLING_ERROR_PREFIX = "eval tooling failed"


def evaluation_payload(eval_result: dict[str, Any] | None, eval_output_dir: Path) -> dict[str, Any]:
    if eval_result is None:
        return {
            "dir": str(eval_output_dir),
            "result_json": "",
            "status": "not-run",
            "scores": {},
        }
    return {
        "dir": str(eval_output_dir),
        "result_json": str(eval_output_dir / "result.json"),
        "status": eval_result.get("status", "failed"),
        "scores": eval_result.get("scores", {}),
        "build_pass": eval_result.get("build_pass"),
        "test_pass": eval_result.get("test_pass"),
    }


def run_status(
    *,
    validation_ok: bool,
    agent_passed: bool,
    submission_exists: bool,
    eval_result: dict[str, Any] | None,
) -> str:
    if not validation_ok:
        return "invalid_task"
    if not submission_exists:
        return "missing_submission"
    if eval_result is None:
        return "not_evaluated"
    if agent_passed and eval_result.get("status") == "passed":
        return "passed"
    return "failed"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def detect_eval_flake(task_run_dir: Path) -> bool:
    """Return True when failure symptoms match known eval infrastructure flakes."""

    logs_dir = task_run_dir / "eval" / "logs"
    if logs_dir.is_dir():
        for name in ("public.stderr", "hidden.stderr", "eval_tooling.stderr", "eval_tooling_retry.stderr"):
            path = logs_dir / name
            if path.is_file() and EVAL_FLAKE_PYTEST_MISSING in path.read_text(encoding="utf-8", errors="ignore"):
                return True

    result_path = task_run_dir / "eval" / "result.json"
    if result_path.is_file():
        try:
            result = json.loads(result_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return False
        errors = result.get("errors")
        if isinstance(errors, list):
            for error in errors:
                if isinstance(error, str) and EVAL_TOOLING_ERROR_PREFIX in error:
                    return True
        eval_tooling = result.get("eval_tooling")
        if isinstance(eval_tooling, dict) and not eval_tooling.get("passed", True):
            return True

    return False


def rebuild_suite_summary(runs: list[dict[str, Any]]) -> dict[str, Any]:
    final_scores = [
        run.get("evaluation", {}).get("scores", {}).get("final_score")
        for run in runs
        if isinstance(run.get("evaluation"), dict)
    ]
    numeric_scores = [score for score in final_scores if isinstance(score, (int, float))]
    return {
        "total": len(runs),
        "passed": sum(1 for run in runs if run.get("status") == "passed"),
        "failed": sum(1 for run in runs if run.get("status") != "passed"),
        "agent_failures": sum(1 for run in runs if not run.get("agent", {}).get("passed", False)),
        "missing_submissions": sum(
            1 for run in runs if not run.get("submission", {}).get("exists", False)
        ),
        "average_final_score": (
            round(sum(numeric_scores) / len(numeric_scores), 6) if numeric_scores else 0.0
        ),
    }


def compact_agent_usage(usage: dict[str, Any]) -> dict[str, Any]:
    if usage.get("available") is not True:
        compact: dict[str, Any] = {
            "available": False,
            "reason": usage.get("reason", "usage unavailable"),
        }
        if isinstance(usage.get("source"), str):
            compact["source"] = usage["source"]
        return compact

    compact = {"available": True}
    for key in (
        "assistant_steps",
        "api_calls",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
    ):
        value = usage.get(key)
        if isinstance(value, int):
            compact[key] = value
    return compact


def compact_suite_run_entry(run: dict[str, Any]) -> dict[str, Any]:
    agent = run.get("agent") if isinstance(run.get("agent"), dict) else {}
    usage = agent.get("usage") if isinstance(agent.get("usage"), dict) else {}
    evaluation = run.get("evaluation") if isinstance(run.get("evaluation"), dict) else {}
    scores = evaluation.get("scores") if isinstance(evaluation.get("scores"), dict) else {}
    return {
        "task_id": run.get("task_id", ""),
        "status": run.get("status", "failed"),
        "run_json": run.get("run_json", ""),
        "result_json": evaluation.get("result_json", ""),
        "final_score": scores.get("final_score", 0.0),
        "agent_usage": compact_agent_usage(usage),
    }
