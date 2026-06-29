"""Shared helpers for suite runs, re-evaluation, and analysis."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EVAL_FLAKE_PYTEST_MISSING = "No module named pytest"
EVAL_TOOLING_ERROR_PREFIX = "eval tooling failed"

ALL_RUN_STATUSES = frozenset(
    {"passed", "failed", "missing_submission", "not_evaluated", "invalid_task"}
)
DEFAULT_RETRY_ONLY_STATUSES = frozenset({"missing_submission", "failed", "not_evaluated"})


def parse_retry_only_statuses(value: str | None) -> frozenset[str]:
    """Parse a comma-separated list of run statuses eligible for agent retry."""

    if not value:
        return DEFAULT_RETRY_ONLY_STATUSES
    statuses = frozenset(part.strip() for part in value.split(",") if part.strip())
    if not statuses:
        return DEFAULT_RETRY_ONLY_STATUSES
    unknown = statuses - ALL_RUN_STATUSES
    if unknown:
        raise ValueError(
            f"unknown retry-only status values: {', '.join(sorted(unknown))}; "
            f"allowed: {', '.join(sorted(ALL_RUN_STATUSES))}"
        )
    return statuses


def load_retained_runs(
    suite_dir: str | Path | None,
    *,
    retain_statuses: frozenset[str] = frozenset({"passed"}),
) -> dict[str, dict[str, Any]]:
    """Load full task run.json payloads from a previous suite output directory."""

    if suite_dir is None:
        return {}
    base_dir = Path(suite_dir).resolve()
    suite_path = base_dir / "suite.json"
    if suite_path.is_file():
        suite = json.loads(suite_path.read_text(encoding="utf-8"))
        retained: dict[str, dict[str, Any]] = {}
        for entry in suite.get("runs", []):
            if not isinstance(entry, dict):
                continue
            status = entry.get("status")
            if not isinstance(status, str) or status not in retain_statuses:
                continue
            task_id = entry.get("task_id")
            if not isinstance(task_id, str) or not task_id:
                continue
            run_json = base_dir / task_id / "run.json"
            if run_json.is_file():
                retained[task_id] = json.loads(run_json.read_text(encoding="utf-8"))
        return retained
    return _load_retained_runs_from_task_dirs(base_dir, retain_statuses=retain_statuses)


def _load_retained_runs_from_task_dirs(
    base_dir: Path,
    *,
    retain_statuses: frozenset[str],
) -> dict[str, dict[str, Any]]:
    """Fallback for mid-suite resume before suite.json is written."""

    retained: dict[str, dict[str, Any]] = {}
    if not base_dir.is_dir():
        return retained
    for task_dir in sorted(base_dir.iterdir()):
        if not task_dir.is_dir():
            continue
        run_json = task_dir / "run.json"
        if not run_json.is_file():
            continue
        try:
            payload = json.loads(run_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        status = payload.get("status")
        if not isinstance(status, str) or status not in retain_statuses:
            continue
        retained[task_dir.name] = payload
    return retained


def evaluation_payload(eval_result: dict[str, Any] | None, eval_output_dir: Path) -> dict[str, Any]:
    if eval_result is None:
        return {
            "dir": str(eval_output_dir),
            "result_json": "",
            "status": "not-run",
            "scores": {},
            "resource_limited": False,
            "log_limit_exceeded": False,
            "docker_sandbox_error": False,
            "sandbox_backend": "",
        }
    sandbox = eval_result.get("sandbox") if isinstance(eval_result.get("sandbox"), dict) else {}
    return {
        "dir": str(eval_output_dir),
        "result_json": str(eval_output_dir / "result.json"),
        "status": eval_result.get("status", "failed"),
        "scores": eval_result.get("scores", {}),
        "build_pass": eval_result.get("build_pass"),
        "test_pass": eval_result.get("test_pass"),
        "resource_limited": _eval_result_has_flag(eval_result, "resource_limited"),
        "log_limit_exceeded": _eval_result_has_flag(eval_result, "log_limit_exceeded"),
        "docker_sandbox_error": bool(
            eval_result.get("docker_sandbox_error") or sandbox.get("docker_sandbox_error")
        ),
        "sandbox_backend": sandbox.get("backend", "") if isinstance(sandbox.get("backend"), str) else "",
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
    by_status: dict[str, int] = {}
    tasks_by_status: dict[str, list[str]] = {}
    for run in runs:
        status = run.get("status", "failed")
        if not isinstance(status, str):
            status = "failed"
        by_status[status] = by_status.get(status, 0) + 1
        task_id = run.get("task_id")
        if isinstance(task_id, str) and task_id:
            tasks_by_status.setdefault(status, []).append(task_id)
    for task_ids in tasks_by_status.values():
        task_ids.sort()
    return {
        "total": len(runs),
        "passed": sum(1 for run in runs if run.get("status") == "passed"),
        "failed": sum(1 for run in runs if run.get("status") != "passed"),
        "agent_failures": sum(1 for run in runs if not run.get("agent", {}).get("passed", False)),
        "missing_submissions": sum(
            1 for run in runs if not run.get("submission", {}).get("exists", False)
        ),
        "recovered_submissions": sum(
            1 for run in runs if run.get("submission", {}).get("recovered", False)
        ),
        "resource_limited_failures": sum(
            1 for run in runs if run.get("evaluation", {}).get("resource_limited") is True
        ),
        "log_limit_failures": sum(
            1 for run in runs if run.get("evaluation", {}).get("log_limit_exceeded") is True
        ),
        "docker_sandbox_failures": sum(
            1 for run in runs if run.get("evaluation", {}).get("docker_sandbox_error") is True
        ),
        "average_final_score": (
            round(sum(numeric_scores) / len(numeric_scores), 6) if numeric_scores else 0.0
        ),
        "by_status": by_status,
        "tasks_by_status": tasks_by_status,
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
    submission = run.get("submission") if isinstance(run.get("submission"), dict) else {}
    entry: dict[str, Any] = {
        "task_id": run.get("task_id", ""),
        "status": run.get("status", "failed"),
        "run_json": run.get("run_json", ""),
        "result_json": evaluation.get("result_json", ""),
        "final_score": scores.get("final_score", 0.0),
        "agent_usage": compact_agent_usage(usage),
    }
    if submission.get("recovered") is True:
        entry["submission_recovered"] = True
    for key in ("resource_limited", "log_limit_exceeded", "docker_sandbox_error", "sandbox_backend"):
        value = evaluation.get(key)
        if value:
            entry[key] = value
    return entry


def _eval_result_has_flag(eval_result: dict[str, Any], flag: str) -> bool:
    if eval_result.get(flag) is True:
        return True
    for key in (
        "dependency_install",
        "eval_tooling",
        "submission_install",
        "build",
        "public_tests",
        "hidden_tests",
    ):
        payload = eval_result.get(key)
        if isinstance(payload, dict) and payload.get(flag) is True:
            return True
    return False
