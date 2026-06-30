"""Agent workspace preparation and end-to-end run orchestration."""

from __future__ import annotations

import json
import re
import shutil
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from dataclasses import dataclass
from datetime import UTC
from datetime import datetime
from pathlib import Path
from typing import Any

from .active_agent_processes import terminate_active_agent_processes
from .agent_adapters import AgentRunConfig
from .agent_adapters import AgentRunContext
from .agent_adapters import get_agent_adapter
from .agent_docker import DEFAULT_AGENT_IMAGE
from .agent_docker import run_agent_in_docker
from .docker_eval import DEFAULT_EVAL_IMAGE
from .docker_eval import evaluate_submission_docker
from .evaluator import evaluate_submission
from .metadata import load_metadata
from .paths import resolve_task_input
from .suite_utils import ALL_RUN_STATUSES
from .suite_utils import DEFAULT_RETRY_ONLY_STATUSES
from .suite_utils import compact_suite_run_entry
from .suite_utils import evaluation_payload as _evaluation_payload
from .suite_utils import load_retained_runs
from .suite_utils import rebuild_suite_summary
from .suite_utils import run_status as _run_status
from .task_discovery import discover_main_task_dirs
from .suite_progress import SuiteBatchProgressManager
from .suite_progress import live_suite_progress
from .validate import validate_task

USAGE_SUM_FIELDS = (
    "assistant_steps",
    "total_messages",
    "api_calls",
    "prompt_tokens",
    "completion_tokens",
    "total_tokens",
    "trace_tokens",
    "billed_tokens",
)

RATE_LIMIT_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"rate limit",
        r"ratelimit",
        r"too many requests",
        r"\b429\b",
        r"quota exceeded",
        r"tpm limit",
    )
)

# SiliconFlow TPM limits use a rolling 60s window; wait long enough to clear it.
RATE_LIMIT_RETRY_WAIT_SECONDS = 65.0


@dataclass(frozen=True)
class _SuiteCheckpointContext:
    output_path: Path
    ordered_task_dirs: list[Path]
    retained_runs: dict[str, dict[str, Any]]
    config: AgentRunConfig
    agent_config_summary: dict[str, Any] | None
    worker_count: int
    retry_rate_limit: int
    retry_only_statuses: frozenset[str]
    extra_agent_passes: int
    max_task_attempts: int | None
    eval_docker: bool
    eval_docker_image: str
    agent_docker: bool
    agent_docker_image: str
    resume_enabled: bool
    suite_source_dir: Path | None
    skipped_max_attempts: frozenset[str]
    runnable_count: int


def run_agent_on_path(
    input_path: str | Path,
    output_dir: str | Path,
    config: AgentRunConfig,
    agent_config_summary: dict[str, Any] | None = None,
    num_workers: int = 1,
    progress: bool = False,
    *,
    task_ids: list[str] | None = None,
    skip_completed_dir: str | Path | None = None,
    retry_rate_limit: int = 1,
    resume_dir: str | Path | None = None,
    resume_mode: bool = False,
    retry_only_statuses: frozenset[str] | None = None,
    extra_agent_passes: int = 0,
    max_task_attempts: int | None = None,
    eval_docker: bool = False,
    eval_docker_image: str = DEFAULT_EVAL_IMAGE,
    agent_docker: bool = False,
    agent_docker_image: str = DEFAULT_AGENT_IMAGE,
) -> dict[str, Any]:
    """Run an agent on one task directory or every task under a dataset root."""

    resolved = resolve_task_input(input_path)
    task_dirs = discover_task_dirs(resolved, task_ids=task_ids)
    output_path = Path(output_dir).resolve()
    if len(task_dirs) == 1 and (resolved / "metadata.json").is_file():
        return run_agent_on_task(
            task_dirs[0],
            output_path,
            config,
            agent_config_summary=agent_config_summary,
            progress=progress,
            eval_docker=eval_docker,
            eval_docker_image=eval_docker_image,
            agent_docker=agent_docker,
            agent_docker_image=agent_docker_image,
        )
    return run_agent_on_suite(
        task_dirs,
        output_path,
        config,
        agent_config_summary=agent_config_summary,
        num_workers=num_workers,
        progress=progress,
        skip_completed_dir=skip_completed_dir,
        retry_rate_limit=retry_rate_limit,
        resume_dir=resume_dir,
        resume_mode=resume_mode,
        retry_only_statuses=retry_only_statuses or DEFAULT_RETRY_ONLY_STATUSES,
        extra_agent_passes=extra_agent_passes,
        max_task_attempts=max_task_attempts,
        eval_docker=eval_docker,
        eval_docker_image=eval_docker_image,
        agent_docker=agent_docker,
        agent_docker_image=agent_docker_image,
    )


def run_agent_on_suite(
    task_dirs: list[Path],
    output_dir: str | Path,
    config: AgentRunConfig,
    agent_config_summary: dict[str, Any] | None = None,
    num_workers: int = 1,
    progress: bool = False,
    skip_completed_dir: str | Path | None = None,
    retry_rate_limit: int = 1,
    resume_dir: str | Path | None = None,
    resume_mode: bool = False,
    retry_only_statuses: frozenset[str] = DEFAULT_RETRY_ONLY_STATUSES,
    extra_agent_passes: int = 0,
    max_task_attempts: int | None = None,
    eval_docker: bool = False,
    eval_docker_image: str = DEFAULT_EVAL_IMAGE,
    agent_docker: bool = False,
    agent_docker_image: str = DEFAULT_AGENT_IMAGE,
) -> dict[str, Any]:
    """Run an agent on multiple tasks and write a suite summary."""

    output_path = Path(output_dir).resolve()
    output_path.mkdir(parents=True, exist_ok=True)
    worker_count = max(1, int(num_workers))
    extra_passes = max(0, int(extra_agent_passes))

    suite_source_dir = _resolve_suite_source_dir(
        output_path=output_path,
        resume_dir=resume_dir,
        resume_mode=resume_mode,
        skip_completed_dir=skip_completed_dir,
    )
    use_resume_retain = resume_mode or resume_dir is not None
    retain_statuses = _resolve_retain_statuses(
        resume_mode=use_resume_retain,
        skip_completed_dir=skip_completed_dir if not use_resume_retain else None,
        retry_only_statuses=retry_only_statuses,
    )
    retained_runs = load_retained_runs(suite_source_dir, retain_statuses=retain_statuses)
    skipped_max_attempts = _tasks_at_max_attempts(
        task_dirs,
        output_path,
        max_task_attempts,
        exclude_task_ids=set(retained_runs),
    )
    retained_runs = _merge_retained_runs(
        retained_runs,
        _load_existing_runs(output_path, skipped_max_attempts),
    )
    runnable_dirs = [
        task_dir
        for task_dir in task_dirs
        if task_dir.name not in retained_runs and task_dir.name not in skipped_max_attempts
    ]

    checkpoint_ctx = _SuiteCheckpointContext(
        output_path=output_path,
        ordered_task_dirs=task_dirs,
        retained_runs=retained_runs,
        config=config,
        agent_config_summary=agent_config_summary,
        worker_count=worker_count,
        retry_rate_limit=max(1, int(retry_rate_limit)),
        retry_only_statuses=retry_only_statuses,
        extra_agent_passes=extra_passes,
        max_task_attempts=max_task_attempts,
        eval_docker=eval_docker,
        eval_docker_image=eval_docker_image,
        agent_docker=agent_docker,
        agent_docker_image=agent_docker_image,
        resume_enabled=use_resume_retain or skip_completed_dir is not None,
        suite_source_dir=suite_source_dir,
        skipped_max_attempts=frozenset(skipped_max_attempts),
        runnable_count=len(runnable_dirs),
    )

    runs = _run_suite_tasks(
        task_dirs=runnable_dirs,
        output_path=output_path,
        config=config,
        agent_config_summary=agent_config_summary,
        num_workers=worker_count,
        progress=progress,
        retry_rate_limit=max(1, int(retry_rate_limit)),
        eval_docker=eval_docker,
        eval_docker_image=eval_docker_image,
        agent_docker=agent_docker,
        agent_docker_image=agent_docker_image,
        checkpoint_ctx=checkpoint_ctx,
    )

    if retained_runs:
        runs = _merge_suite_runs(task_dirs, runs, retained_runs)

    for pass_index in range(extra_passes):
        runs_by_id = {
            run.get("task_id"): run for run in runs if isinstance(run.get("task_id"), str)
        }
        retry_dirs = [
            task_dir
            for task_dir in task_dirs
            if runs_by_id.get(task_dir.name, {}).get("status") in retry_only_statuses
            and task_dir.name not in skipped_max_attempts
            and not _task_at_max_attempts(output_path / task_dir.name, max_task_attempts)
        ]
        if not retry_dirs:
            break
        retained = {
            task_id: run
            for task_id, run in runs_by_id.items()
            if run.get("status") not in retry_only_statuses
        }
        fresh_runs = _run_suite_tasks(
            task_dirs=retry_dirs,
            output_path=output_path,
            config=config,
            agent_config_summary=agent_config_summary,
            num_workers=worker_count,
            progress=progress,
            retry_rate_limit=max(1, int(retry_rate_limit)),
            eval_docker=eval_docker,
            eval_docker_image=eval_docker_image,
            agent_docker=agent_docker,
            agent_docker_image=agent_docker_image,
        )
        runs = _merge_suite_runs(task_dirs, fresh_runs, retained)
        snapshot_path = output_path / f"suite.pass{pass_index + 1}.json"
        _write_suite_snapshot(
            snapshot_path,
            runs=runs,
            config=config,
            agent_config_summary=agent_config_summary,
            output_path=output_path,
            worker_count=worker_count,
            retry_rate_limit=max(1, int(retry_rate_limit)),
            retry_only_statuses=retry_only_statuses,
            extra_agent_passes=extra_passes,
            pass_index=pass_index + 1,
            agent_docker=agent_docker,
            agent_docker_image=agent_docker_image,
        )

    summary = rebuild_suite_summary(runs)
    agent_usage_totals = _sum_agent_usage(runs)
    result = {
        "mode": "suite",
        "generated_at": _utc_now(),
        "agent": config.agent,
        "agent_config": agent_config_summary or {},
        "output_dir": str(output_path),
        "num_workers": worker_count,
        "agent_backend": "docker" if agent_docker else "local",
        "agent_docker_image": agent_docker_image if agent_docker else "",
        "eval_backend": "docker" if eval_docker else "local",
        "eval_docker_image": eval_docker_image if eval_docker else "",
        "retry_rate_limit": max(1, int(retry_rate_limit)),
        "retry_only_statuses": sorted(retry_only_statuses),
        "extra_agent_passes": extra_passes,
        "max_task_attempts": max_task_attempts,
        "skipped_completed": sorted(retained_runs),
        "resume": {
            "enabled": resume_mode or resume_dir is not None or skip_completed_dir is not None,
            "source_dir": str(suite_source_dir) if suite_source_dir is not None else "",
            "retained": len(retained_runs),
            "retried": len(runnable_dirs),
            "skipped_max_attempts": sorted(skipped_max_attempts),
        },
        "summary": summary,
        "agent_usage_totals": agent_usage_totals,
        "runs": [compact_suite_run_entry(run) for run in runs],
    }
    (output_path / "suite.json").write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return result


def run_agent_on_task(
    task_dir: str | Path,
    output_dir: str | Path,
    config: AgentRunConfig,
    agent_config_summary: dict[str, Any] | None = None,
    *,
    progress: bool = False,
    eval_docker: bool = False,
    eval_docker_image: str = DEFAULT_EVAL_IMAGE,
    agent_docker: bool = False,
    agent_docker_image: str = DEFAULT_AGENT_IMAGE,
) -> dict[str, Any]:
    """Run an agent on a single task, collect its submission, and evaluate it."""

    use_live_progress = progress and sys.stderr.isatty()
    if use_live_progress:
        task_path = Path(task_dir).resolve()
        output_path = Path(output_dir).resolve()
        validation = validate_task(task_path)
        task_id = validation.task_id
        if validation.valid:
            metadata = load_metadata(task_path).data
            task_id = metadata.get("task_id", task_id)
        with live_suite_progress(num_tasks=1, output_dir=output_path, layout="flat") as progress_manager:
            progress_manager.on_task_start(task_id)
            progress_manager.update_task_status(task_id, "preparing workspace")
            result = _run_agent_on_task_body(
                task_dir=task_dir,
                output_dir=output_dir,
                config=config,
                agent_config_summary=agent_config_summary,
                eval_docker=eval_docker,
                eval_docker_image=eval_docker_image,
                agent_docker=agent_docker,
                agent_docker_image=agent_docker_image,
            )
            progress_manager.on_task_end(task_id, result.get("status"))
            return result

    return _run_agent_on_task_body(
        task_dir=task_dir,
        output_dir=output_dir,
        config=config,
        agent_config_summary=agent_config_summary,
        eval_docker=eval_docker,
        eval_docker_image=eval_docker_image,
        agent_docker=agent_docker,
        agent_docker_image=agent_docker_image,
        progress=progress,
    )


def _run_agent_on_task_body(
    task_dir: str | Path,
    output_dir: str | Path,
    config: AgentRunConfig,
    agent_config_summary: dict[str, Any] | None = None,
    *,
    progress: bool = False,
    eval_docker: bool = False,
    eval_docker_image: str = DEFAULT_EVAL_IMAGE,
    agent_docker: bool = False,
    agent_docker_image: str = DEFAULT_AGENT_IMAGE,
) -> dict[str, Any]:

    task_path = Path(task_dir).resolve()
    output_path = Path(output_dir).resolve()
    output_path.mkdir(parents=True, exist_ok=True)

    next_attempt, previous_attempt_json = _archive_previous_run(output_path)

    workspace_dir = output_path / "workspace"
    agent_output_dir = output_path / "agent"
    collected_submission_dir = output_path / "submission"
    eval_output_dir = output_path / "eval"
    for path in (workspace_dir, agent_output_dir, collected_submission_dir, eval_output_dir):
        _reset_dir(path)

    errors: list[str] = []
    validation = validate_task(task_path)
    task_id = validation.task_id
    metadata: dict[str, Any] = {}
    if not validation.valid:
        errors.extend(f"invalid task: {error}" for error in validation.errors)
    else:
        metadata = load_metadata(task_path).data
        task_id = metadata.get("task_id", task_id)

    if progress:
        _progress(True, f"started {task_id}")

    agent_result = None
    eval_result = None
    recovery_info: dict[str, Any] | None = None
    workspace_submission_dir = workspace_dir / "submission"
    stdout_log = agent_output_dir / "stdout.log"
    stderr_log = agent_output_dir / "stderr.log"

    if validation.valid:
        task_file = prepare_agent_workspace(task_path, workspace_dir, metadata)
        prompt_path = agent_output_dir / "prompt.txt"
        prompt_path.write_text(task_file.read_text(encoding="utf-8"), encoding="utf-8")

        context = AgentRunContext(
            workspace_dir=workspace_dir,
            task_file=task_file,
            submission_dir=workspace_submission_dir,
            agent_output_dir=agent_output_dir,
            task_text=task_file.read_text(encoding="utf-8"),
        )
        try:
            if agent_docker:
                agent_result = run_agent_in_docker(
                    context,
                    config,
                    image=agent_docker_image,
                    stdout_log=stdout_log,
                    stderr_log=stderr_log,
                )
            else:
                adapter = get_agent_adapter(config.agent)
                agent_result = adapter.run(
                    context,
                    config,
                    stdout_log=stdout_log,
                    stderr_log=stderr_log,
                )
        except ValueError as exc:
            errors.append(str(exc))
        if agent_result is not None and not stdout_log.is_file():
            _write_agent_logs(agent_output_dir, agent_result)

        if _has_submission_files(workspace_submission_dir):
            _copy_submission(workspace_submission_dir, collected_submission_dir)
            eval_result = _evaluate_collected_submission(
                task_path=task_path,
                collected_submission_dir=collected_submission_dir,
                eval_output_dir=eval_output_dir,
                eval_docker=eval_docker,
                eval_docker_image=eval_docker_image,
            )
        else:
            recovery_info = _recover_misplaced_submission(workspace_dir, workspace_submission_dir)
            if recovery_info is not None and recovery_info.get("message"):
                errors.append(str(recovery_info["message"]))
            if _has_submission_files(workspace_submission_dir):
                _copy_submission(workspace_submission_dir, collected_submission_dir)
                eval_result = _evaluate_collected_submission(
                    task_path=task_path,
                    collected_submission_dir=collected_submission_dir,
                    eval_output_dir=eval_output_dir,
                    eval_docker=eval_docker,
                    eval_docker_image=eval_docker_image,
                )
            else:
                errors.append("agent did not create any files under workspace/submission")
                errors.append(_missing_submission_diagnostic(workspace_dir))

    agent_payload: dict[str, Any]
    if agent_result is None:
        agent_payload = {
            "name": config.agent,
            "command": [],
            "returncode": None,
            "passed": False,
            "duration_seconds": 0.0,
            "timed_out": False,
            "reason": "",
            "resource_limited": False,
            "stdout_truncated": False,
            "stderr_truncated": False,
            "log_limit_exceeded": False,
            "stdout_log": str(stdout_log),
            "stderr_log": str(stderr_log),
        }
    else:
        agent_payload = agent_result.payload(stdout_log=stdout_log, stderr_log=stderr_log)
    agent_payload["usage"] = _collect_agent_usage(config.agent, agent_output_dir)

    submission_exists = _has_submission_files(collected_submission_dir)
    evaluation_payload = _evaluation_payload(eval_result, eval_output_dir)
    status = _run_status(
        validation_ok=validation.valid,
        agent_passed=agent_payload["passed"],
        submission_exists=submission_exists,
        eval_result=eval_result,
    )
    run_json_path = output_path / "run.json"
    submission_payload: dict[str, Any] = {
        "dir": str(collected_submission_dir),
        "exists": submission_exists,
        "recovered": bool(recovery_info and recovery_info.get("recovered")),
    }
    recovery_sources = recovery_info.get("recovery_sources") if isinstance(recovery_info, dict) else None
    if isinstance(recovery_sources, list) and recovery_sources:
        submission_payload["recovery_sources"] = recovery_sources
    result = {
        "mode": "task",
        "generated_at": _utc_now(),
        "task_id": task_id,
        "status": status,
        "attempt": next_attempt,
        "agent": agent_payload,
        "agent_backend": "docker" if agent_docker else "local",
        "agent_docker_image": agent_docker_image if agent_docker else "",
        "agent_config": agent_config_summary or {},
        "workspace": {
            "dir": str(workspace_dir),
            "task_file": str(workspace_dir / "TASK.md"),
        },
        "submission": submission_payload,
        "evaluation": evaluation_payload,
        "eval_backend": "docker" if eval_docker else "local",
        "eval_docker_image": eval_docker_image if eval_docker else "",
        "errors": errors,
        "run_json": str(run_json_path),
    }
    if previous_attempt_json is not None:
        result["previous_attempt_json"] = previous_attempt_json
    run_json_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    if progress:
        _progress(True, f"finished {task_id}: {status}")
    return result


def _evaluate_collected_submission(
    *,
    task_path: Path,
    collected_submission_dir: Path,
    eval_output_dir: Path,
    eval_docker: bool,
    eval_docker_image: str,
) -> dict[str, Any]:
    if eval_docker:
        return evaluate_submission_docker(
            task_path,
            collected_submission_dir,
            eval_output_dir,
            image=eval_docker_image,
            use_docker=True,
        )
    return evaluate_submission(task_path, collected_submission_dir, eval_output_dir)


def _run_suite_tasks(
    *,
    task_dirs: list[Path],
    output_path: Path,
    config: AgentRunConfig,
    agent_config_summary: dict[str, Any] | None,
    num_workers: int,
    progress: bool,
    retry_rate_limit: int = 1,
    eval_docker: bool = False,
    eval_docker_image: str = DEFAULT_EVAL_IMAGE,
    agent_docker: bool = False,
    agent_docker_image: str = DEFAULT_AGENT_IMAGE,
    checkpoint_ctx: _SuiteCheckpointContext | None = None,
) -> list[dict[str, Any]]:
    total = len(task_dirs)
    use_live_progress = progress and sys.stderr.isatty() and total >= 1

    if use_live_progress:
        with live_suite_progress(num_tasks=total, output_dir=output_path) as progress_manager:
            return _execute_suite_tasks(
                task_dirs=task_dirs,
                output_path=output_path,
                config=config,
                agent_config_summary=agent_config_summary,
                num_workers=num_workers,
                total=total,
                progress_manager=progress_manager,
                retry_rate_limit=retry_rate_limit,
                eval_docker=eval_docker,
                eval_docker_image=eval_docker_image,
                agent_docker=agent_docker,
                agent_docker_image=agent_docker_image,
                checkpoint_ctx=checkpoint_ctx,
            )

    return _execute_suite_tasks(
        task_dirs=task_dirs,
        output_path=output_path,
        config=config,
        agent_config_summary=agent_config_summary,
        num_workers=num_workers,
        total=total,
        progress=progress,
        progress_manager=None,
        retry_rate_limit=retry_rate_limit,
        eval_docker=eval_docker,
        eval_docker_image=eval_docker_image,
        agent_docker=agent_docker,
        agent_docker_image=agent_docker_image,
        checkpoint_ctx=checkpoint_ctx,
    )


def _execute_suite_tasks(
    *,
    task_dirs: list[Path],
    output_path: Path,
    config: AgentRunConfig,
    agent_config_summary: dict[str, Any] | None,
    num_workers: int,
    total: int,
    progress: bool = False,
    progress_manager: SuiteBatchProgressManager | None = None,
    retry_rate_limit: int = 1,
    eval_docker: bool = False,
    eval_docker_image: str = DEFAULT_EVAL_IMAGE,
    agent_docker: bool = False,
    agent_docker_image: str = DEFAULT_AGENT_IMAGE,
    checkpoint_ctx: _SuiteCheckpointContext | None = None,
) -> list[dict[str, Any]]:
    if num_workers == 1:
        runs = []
        try:
            for index, task_dir in enumerate(task_dirs, start=1):
                runs.append(
                    _run_suite_task_safely(
                        index=index,
                        total=total,
                        task_dir=task_dir,
                        output_path=output_path,
                        config=config,
                        agent_config_summary=agent_config_summary,
                        progress=progress and progress_manager is None,
                        progress_manager=progress_manager,
                        retry_rate_limit=retry_rate_limit,
                        eval_docker=eval_docker,
                        eval_docker_image=eval_docker_image,
                        agent_docker=agent_docker,
                        agent_docker_image=agent_docker_image,
                    )
                )
                if checkpoint_ctx is not None:
                    _write_suite_checkpoint(checkpoint_ctx, runs)
        except KeyboardInterrupt:
            _stop_suite_run()
            raise SystemExit(130) from None
        return runs

    runs_by_index: dict[int, dict[str, Any]] = {}
    executor = ThreadPoolExecutor(max_workers=num_workers)
    futures = {
        executor.submit(
            _run_suite_task_safely,
            index=index,
            total=total,
            task_dir=task_dir,
            output_path=output_path,
            config=config,
            agent_config_summary=agent_config_summary,
            progress=progress and progress_manager is None,
            progress_manager=progress_manager,
            retry_rate_limit=retry_rate_limit,
            eval_docker=eval_docker,
            eval_docker_image=eval_docker_image,
            agent_docker=agent_docker,
            agent_docker_image=agent_docker_image,
        ): index
        for index, task_dir in enumerate(task_dirs, start=1)
    }
    try:
        for future in as_completed(futures):
            index = futures[future]
            try:
                runs_by_index[index] = future.result()
            except Exception as exc:  # Defensive: keep suite output complete.
                task_dir = task_dirs[index - 1]
                runs_by_index[index] = _exception_run_result(
                    task_dir,
                    output_path / task_dir.name,
                    config,
                    agent_config_summary,
                    exc,
                    progress_manager=progress_manager,
                    agent_docker=agent_docker,
                    agent_docker_image=agent_docker_image,
                )
            if checkpoint_ctx is not None:
                completed = [runs_by_index[i] for i in sorted(runs_by_index)]
                _write_suite_checkpoint(checkpoint_ctx, completed)
    except KeyboardInterrupt:
        _stop_suite_run()
        for future in futures:
            future.cancel()
        executor.shutdown(wait=False, cancel_futures=True)
        raise SystemExit(130) from None
    else:
        executor.shutdown(wait=True)
    return [runs_by_index[index] for index in range(1, total + 1)]


def _stop_suite_run() -> None:
    print("\nStopping suite run and terminating active agent processes...", file=sys.stderr, flush=True)
    terminate_active_agent_processes()


def _run_suite_task_safely(
    *,
    index: int,
    total: int,
    task_dir: Path,
    output_path: Path,
    config: AgentRunConfig,
    agent_config_summary: dict[str, Any] | None,
    progress: bool,
    progress_manager: SuiteBatchProgressManager | None = None,
    retry_rate_limit: int = 1,
    eval_docker: bool = False,
    eval_docker_image: str = DEFAULT_EVAL_IMAGE,
    agent_docker: bool = False,
    agent_docker_image: str = DEFAULT_AGENT_IMAGE,
) -> dict[str, Any]:
    task_id = task_dir.name
    if progress_manager is not None:
        progress_manager.on_task_start(task_id)
        progress_manager.update_task_status(task_id, "preparing workspace")
    else:
        _progress(progress, f"[{index}/{total}] started {task_id}")

    run_output = output_path / task_id
    try:
        result = _run_suite_task_with_retries(
            task_dir=task_dir,
            run_output=run_output,
            config=config,
            agent_config_summary=agent_config_summary,
            max_attempts=retry_rate_limit,
            eval_docker=eval_docker,
            eval_docker_image=eval_docker_image,
            agent_docker=agent_docker,
            agent_docker_image=agent_docker_image,
        )
    except Exception as exc:  # Defensive: one task should not abort the suite.
        result = _exception_run_result(
            task_dir,
            run_output,
            config,
            agent_config_summary,
            exc,
            progress_manager=progress_manager,
            agent_docker=agent_docker,
            agent_docker_image=agent_docker_image,
        )

    status = result.get("status", "failed")
    if progress_manager is not None:
        progress_manager.on_task_end(task_id, status)
    else:
        _progress(progress, f"[{index}/{total}] finished {task_id}: {status}")
    return result


def _exception_run_result(
    task_dir: Path,
    output_dir: Path,
    config: AgentRunConfig,
    agent_config_summary: dict[str, Any] | None,
    exc: Exception,
    progress_manager: SuiteBatchProgressManager | None = None,
    agent_docker: bool = False,
    agent_docker_image: str = DEFAULT_AGENT_IMAGE,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    run_json_path = output_dir / "run.json"
    result = {
        "mode": "task",
        "generated_at": _utc_now(),
        "task_id": task_dir.name,
        "status": "failed",
        "agent": {
            "name": config.agent,
            "command": [],
            "returncode": None,
            "passed": False,
            "duration_seconds": 0.0,
            "timed_out": False,
            "reason": "suite task raised an exception",
            "resource_limited": False,
            "stdout_truncated": False,
            "stderr_truncated": False,
            "log_limit_exceeded": False,
            "usage": _unavailable_agent_usage(output_dir / "agent" / "usage.json", "task raised before usage was available"),
        },
        "agent_backend": "docker" if agent_docker else "local",
        "agent_docker_image": agent_docker_image if agent_docker else "",
        "agent_config": agent_config_summary or {},
        "workspace": {
            "dir": str(output_dir / "workspace"),
            "task_file": str(output_dir / "workspace" / "TASK.md"),
        },
        "submission": {
            "dir": str(output_dir / "submission"),
            "exists": False,
        },
        "evaluation": {
            "dir": str(output_dir / "eval"),
            "result_json": "",
            "status": "not-run",
            "scores": {},
        },
        "errors": [
            f"{type(exc).__name__}: {exc}",
            traceback.format_exc(),
        ],
        "run_json": str(run_json_path),
    }
    run_json_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result


def _progress(enabled: bool, message: str) -> None:
    if enabled:
        print(message, file=sys.stderr, flush=True)


def discover_task_dirs(input_path: str | Path, task_ids: list[str] | None = None) -> list[Path]:
    """Discover task directories from either a task dir or a dataset root."""

    path = resolve_task_input(input_path)
    hard_only = path.resolve() == resolve_task_input("benchmark/tasks").resolve()
    return discover_main_task_dirs(path, task_ids=task_ids, hard_only=hard_only)


def load_skipped_runs(skip_dir: str | Path | None) -> dict[str, dict[str, Any]]:
    """Load passed task run.json payloads from a previous suite output directory."""

    return load_retained_runs(skip_dir, retain_statuses=frozenset({"passed"}))


def _resolve_suite_source_dir(
    *,
    output_path: Path,
    resume_dir: str | Path | None,
    resume_mode: bool,
    skip_completed_dir: str | Path | None,
) -> Path | None:
    if resume_dir is not None:
        return Path(resume_dir).resolve()
    if resume_mode:
        return output_path
    if skip_completed_dir is not None:
        return Path(skip_completed_dir).resolve()
    return None


def _resolve_retain_statuses(
    *,
    resume_mode: bool,
    skip_completed_dir: str | Path | None,
    retry_only_statuses: frozenset[str],
) -> frozenset[str]:
    if resume_mode:
        return ALL_RUN_STATUSES - retry_only_statuses
    if skip_completed_dir is not None:
        return frozenset({"passed"})
    return frozenset()


def _load_existing_runs(output_path: Path, task_ids: set[str]) -> dict[str, dict[str, Any]]:
    runs: dict[str, dict[str, Any]] = {}
    for task_id in sorted(task_ids):
        run_json = output_path / task_id / "run.json"
        if not run_json.is_file():
            continue
        try:
            payload = json.loads(run_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            runs[task_id] = payload
    return runs


def _merge_retained_runs(
    primary: dict[str, dict[str, Any]],
    secondary: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    merged = dict(primary)
    for task_id, run in secondary.items():
        merged.setdefault(task_id, run)
    return merged


def _read_task_attempt(task_run_dir: Path) -> int:
    run_json_path = task_run_dir / "run.json"
    if not run_json_path.is_file():
        return 0
    try:
        data = json.loads(run_json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return 0
    attempt = data.get("attempt", 1)
    if isinstance(attempt, int) and attempt >= 1:
        return attempt
    return 1


def _task_at_max_attempts(task_run_dir: Path, max_task_attempts: int | None) -> bool:
    if max_task_attempts is None or max_task_attempts < 1:
        return False
    return _read_task_attempt(task_run_dir) >= max_task_attempts


def _tasks_at_max_attempts(
    task_dirs: list[Path],
    output_path: Path,
    max_task_attempts: int | None,
    *,
    exclude_task_ids: set[str],
) -> set[str]:
    if max_task_attempts is None or max_task_attempts < 1:
        return set()
    skipped: set[str] = set()
    for task_dir in task_dirs:
        task_id = task_dir.name
        if task_id in exclude_task_ids:
            continue
        if _task_at_max_attempts(output_path / task_id, max_task_attempts):
            skipped.add(task_id)
    return skipped


def _archive_previous_run(output_path: Path) -> tuple[int, str | None]:
    run_json_path = output_path / "run.json"
    if not run_json_path.is_file():
        return 1, None
    try:
        data = json.loads(run_json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return 1, None
    current_attempt = data.get("attempt", 1)
    if not isinstance(current_attempt, int) or current_attempt < 1:
        current_attempt = 1
    archive_name = f"run.attempt{current_attempt}.json"
    archive_path = output_path / archive_name
    shutil.copy2(run_json_path, archive_path)
    return current_attempt + 1, str(archive_path)


def _write_suite_snapshot(
    snapshot_path: Path,
    *,
    runs: list[dict[str, Any]],
    config: AgentRunConfig,
    agent_config_summary: dict[str, Any] | None,
    output_path: Path,
    worker_count: int,
    retry_rate_limit: int,
    retry_only_statuses: frozenset[str],
    extra_agent_passes: int,
    pass_index: int,
    agent_docker: bool = False,
    agent_docker_image: str = DEFAULT_AGENT_IMAGE,
) -> None:
    snapshot = {
        "mode": "suite_snapshot",
        "generated_at": _utc_now(),
        "pass_index": pass_index,
        "agent": config.agent,
        "agent_backend": "docker" if agent_docker else "local",
        "agent_docker_image": agent_docker_image if agent_docker else "",
        "output_dir": str(output_path),
        "retry_only_statuses": sorted(retry_only_statuses),
        "extra_agent_passes": extra_agent_passes,
        "summary": rebuild_suite_summary(runs),
        "runs": [compact_suite_run_entry(run) for run in runs],
        "num_workers": worker_count,
        "retry_rate_limit": retry_rate_limit,
        "agent_config": agent_config_summary or {},
    }
    snapshot_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True), encoding="utf-8")


def _write_suite_checkpoint(
    ctx: _SuiteCheckpointContext,
    completed_fresh_runs: list[dict[str, Any]],
) -> None:
    merged = _merge_suite_runs(ctx.ordered_task_dirs, completed_fresh_runs, ctx.retained_runs)
    agent_usage_totals = _sum_agent_usage(merged)
    payload = {
        "mode": "suite",
        "checkpoint": True,
        "generated_at": _utc_now(),
        "agent": ctx.config.agent,
        "agent_config": ctx.agent_config_summary or {},
        "output_dir": str(ctx.output_path),
        "num_workers": ctx.worker_count,
        "agent_backend": "docker" if ctx.agent_docker else "local",
        "agent_docker_image": ctx.agent_docker_image if ctx.agent_docker else "",
        "eval_backend": "docker" if ctx.eval_docker else "local",
        "eval_docker_image": ctx.eval_docker_image if ctx.eval_docker else "",
        "retry_rate_limit": ctx.retry_rate_limit,
        "retry_only_statuses": sorted(ctx.retry_only_statuses),
        "extra_agent_passes": ctx.extra_agent_passes,
        "max_task_attempts": ctx.max_task_attempts,
        "skipped_completed": sorted(ctx.retained_runs),
        "resume": {
            "enabled": ctx.resume_enabled,
            "source_dir": str(ctx.suite_source_dir) if ctx.suite_source_dir is not None else "",
            "retained": len(ctx.retained_runs),
            "retried": ctx.runnable_count,
            "skipped_max_attempts": sorted(ctx.skipped_max_attempts),
        },
        "summary": rebuild_suite_summary(merged),
        "agent_usage_totals": agent_usage_totals,
        "runs": [compact_suite_run_entry(run) for run in merged],
        "checkpoint_progress": {
            "completed_this_run": len(completed_fresh_runs),
            "runnable_total": ctx.runnable_count,
        },
    }
    (ctx.output_path / "suite.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _merge_suite_runs(
    ordered_task_dirs: list[Path],
    fresh_runs: list[dict[str, Any]],
    skipped_runs: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    fresh_by_id = {
        run.get("task_id"): run for run in fresh_runs if isinstance(run.get("task_id"), str)
    }
    merged: list[dict[str, Any]] = []
    for task_dir in ordered_task_dirs:
        task_id = task_dir.name
        if task_id in skipped_runs:
            merged.append(skipped_runs[task_id])
        elif task_id in fresh_by_id:
            merged.append(fresh_by_id[task_id])
    return merged


def _run_suite_task_with_retries(
    *,
    task_dir: Path,
    run_output: Path,
    config: AgentRunConfig,
    agent_config_summary: dict[str, Any] | None,
    max_attempts: int = 1,
    eval_docker: bool = False,
    eval_docker_image: str = DEFAULT_EVAL_IMAGE,
    agent_docker: bool = False,
    agent_docker_image: str = DEFAULT_AGENT_IMAGE,
) -> dict[str, Any]:
    attempts = max(1, int(max_attempts))
    result: dict[str, Any] = {}
    for attempt in range(attempts):
        result = run_agent_on_task(
            task_dir,
            run_output,
            config,
            agent_config_summary=agent_config_summary,
            eval_docker=eval_docker,
            eval_docker_image=eval_docker_image,
            agent_docker=agent_docker,
            agent_docker_image=agent_docker_image,
        )
        if result.get("status") == "passed" or not _is_rate_limit_failure(result):
            return result
        if attempt < attempts - 1:
            task_id = result.get("task_id", task_dir.name)
            print(
                f"Rate limit on {task_id}; retrying in {RATE_LIMIT_RETRY_WAIT_SECONDS:.0f}s "
                f"(attempt {attempt + 2}/{attempts})...",
                file=sys.stderr,
                flush=True,
            )
            time.sleep(RATE_LIMIT_RETRY_WAIT_SECONDS)
    return result


def _is_rate_limit_failure(result: dict[str, Any]) -> bool:
    chunks: list[str] = []
    agent = result.get("agent")
    if isinstance(agent, dict):
        usage = agent.get("usage")
        if isinstance(usage, dict):
            exit_status = usage.get("exit_status")
            if isinstance(exit_status, str) and exit_status:
                chunks.append(exit_status)
        for key in ("reason",):
            value = agent.get(key)
            if isinstance(value, str):
                chunks.append(value)
        for log_key in ("stderr_log", "stdout_log"):
            log_path = agent.get(log_key)
            if isinstance(log_path, str):
                path = Path(log_path)
                if path.is_file():
                    chunks.append(path.read_text(encoding="utf-8", errors="replace"))
    errors = result.get("errors")
    if isinstance(errors, list):
        chunks.extend(str(item) for item in errors)
    text = "\n".join(chunks)
    return any(pattern.search(text) for pattern in RATE_LIMIT_PATTERNS)


def prepare_agent_workspace(task_dir: str | Path, workspace_dir: str | Path, metadata: dict[str, Any]) -> Path:
    """Build the redacted workspace visible to the agent and return TASK.md."""

    task_path = Path(task_dir).resolve()
    workspace_path = Path(workspace_dir).resolve()
    workspace_path.mkdir(parents=True, exist_ok=True)

    _copy_path(task_path / "repo", workspace_path / "repo")
    _copy_path(task_path / _test_path(metadata, "public", "public_tests/"), workspace_path / "public_tests")
    lock_path = task_path / _dependency_lock(metadata)
    if lock_path.exists():
        shutil.copy2(lock_path, workspace_path / "requirements.lock")
    else:
        (workspace_path / "requirements.lock").write_text("", encoding="utf-8")

    redacted_metadata = redact_task_metadata(metadata)
    (workspace_path / "metadata.json").write_text(
        json.dumps(redacted_metadata, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (workspace_path / "submission").mkdir(exist_ok=True)
    task_file = workspace_path / "TASK.md"
    task_file.write_text(build_task_prompt(redacted_metadata), encoding="utf-8")
    return task_file


def redact_task_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    """Return the metadata subset that is safe and useful for an agent."""

    environment = metadata.get("environment") if isinstance(metadata.get("environment"), dict) else {}
    tests = metadata.get("tests") if isinstance(metadata.get("tests"), dict) else {}
    return {
        "task_id": metadata.get("task_id", ""),
        "language": metadata.get("language", ""),
        "difficulty": metadata.get("difficulty", ""),
        "tags": metadata.get("tags", []),
        "source": metadata.get("source", {}),
        "feature": metadata.get("feature", {}),
        "entanglement": metadata.get("entanglement", {}),
        "output": metadata.get("output", {}),
        "environment": {
            "python": environment.get("python", ""),
            "network": environment.get("network", False),
            "timeout_seconds": environment.get("timeout_seconds", 0),
            "dependency_lock": environment.get("dependency_lock", "requirements.lock"),
            "allowed_dependencies": environment.get("allowed_dependencies", []),
            "forbidden_dependencies": environment.get("forbidden_dependencies", []),
            "forbidden_imports": environment.get("forbidden_imports", []),
        },
        "tests": {
            "public": "public_tests/",
            "command": tests.get("command", "pytest"),
        },
    }


def build_task_prompt(metadata: dict[str, Any]) -> str:
    """Build the task prompt given to the agent."""

    feature = metadata.get("feature", {}) if isinstance(metadata.get("feature"), dict) else {}
    output = metadata.get("output", {}) if isinstance(metadata.get("output"), dict) else {}
    entanglement = (
        metadata.get("entanglement", {}) if isinstance(metadata.get("entanglement"), dict) else {}
    )
    environment = (
        metadata.get("environment", {}) if isinstance(metadata.get("environment"), dict) else {}
    )
    source = metadata.get("source", {}) if isinstance(metadata.get("source"), dict) else {}
    tags = _format_list(metadata.get("tags", []))
    entanglement_types = _format_list(entanglement.get("types", []))
    entanglement_signals = _format_list(entanglement.get("signals", []))
    included = _format_list(feature.get("included_behaviors", []))
    excluded = _format_list(feature.get("excluded_behaviors", []))
    entrypoints = _format_list(feature.get("source_entrypoints", []))
    allowed_dependencies = _format_list(environment.get("allowed_dependencies", []))
    forbidden_dependencies = _format_list(environment.get("forbidden_dependencies", []))
    forbidden_imports = _format_list(environment.get("forbidden_imports", []))
    forbidden_import_names = [
        item.strip("- ").strip()
        for item in (environment.get("forbidden_imports") or [])
        if isinstance(item, str) and item.strip()
    ]
    forbidden_grep = " ".join(forbidden_import_names[:5]) or "original package names"

    return (
        f"# FeatureLiftBench Task: {metadata.get('task_id', '')}\n\n"
        "You are in a FeatureLiftBench agent workspace. Decouple the requested feature from "
        "`repo/` into a standalone, installable Python package under `submission/`.\n\n"
        "## How to work\n\n"
        "1. Read `source entrypoints` and the full **Required Output API** below — implement every "
        "listed import path, not just the primary callable.\n"
        "2. Copy the smallest **behavior-complete** implementation closure from `repo/` "
        "into `submission/featurelifted/`.\n"
        "3. Rewrite imports so runtime code uses `featurelifted` only — never the original package.\n"
        f"4. Before submitting, grep your submission for forbidden imports, e.g. "
        f"`grep -R \"import \" submission/ | grep -E '({forbidden_grep})'` — any match fails evaluation.\n"
        "5. Run `pytest public_tests/` in the workspace and fix failures.\n"
        "6. **Public tests passing does not mean you are done.** The evaluator also runs hidden tests "
        "and stricter checks you cannot see here.\n"
        "7. Before submitting, verify your package is under `submission/featurelifted/`, e.g. "
        "`test -d submission/featurelifted && ls submission/featurelifted | head`.\n"
        "8. Do **not** put your package in `featurelifted/` at the workspace root — only "
        "`submission/featurelifted/` counts.\n"
        "9. When confident, submit with the command at the bottom.\n\n"
        "## Workspace\n\n"
        "- `repo/`: source repository snapshot for the fixed commit.\n"
        "- `public_tests/`: tests you may run while developing.\n"
        "- `requirements.lock`: locked third-party runtime dependencies allowed by the task.\n"
        "- `metadata.json`: redacted task metadata. Hidden tests and evaluator internals are not present.\n"
        "- `submission/`: write your final package here.\n\n"
        "## Closure Discipline\n\n"
        "- Treat the target as a real extracted feature, not a toy rewrite for public tests.\n"
        "- Start from source entrypoints, follow imports, helpers, constants, data files, "
        "exceptions, and resources needed for the included behaviors, then trim unrelated "
        "package areas.\n"
        "- Every copied file should support target behavior, public API compatibility, an "
        "exception/type/resource, or a transitive helper used by that behavior.\n"
        "- Remove tests, docs, CLI, network/runtime subsystems, and unrelated adapters unless "
        "the feature specification needs them.\n"
        "- If public tests pass with a shallow rewrite, still inspect included behaviors and "
        "hidden-risk edge cases before submitting.\n\n"
        "## Source\n\n"
        f"- Name: {source.get('name', '')}\n"
        f"- URL: {source.get('url', '')}\n"
        f"- Commit: {source.get('commit', '')}\n"
        f"- License: {source.get('license', '')}\n\n"
        "## Target Feature\n\n"
        f"- Name: {feature.get('name', '')}\n"
        f"- Difficulty: {metadata.get('difficulty', '')}\n"
        f"- Tags:\n{tags}\n"
        f"- Description: {feature.get('description', '')}\n"
        f"- Source entrypoints:\n{entrypoints}\n"
        f"- Included behaviors:\n{included}\n"
        f"- Excluded behaviors:\n{excluded}\n"
        "## Entanglement Context\n\n"
        f"- Level: {entanglement.get('level', '')}\n"
        f"- Types:\n{entanglement_types}\n"
        f"- Description: {entanglement.get('description', '')}\n"
        f"- Signals:\n{entanglement_signals}\n"
        "## Required Output API\n\n"
        f"- Package: `{output.get('package', 'featurelifted')}`\n"
        f"- Import: `{output.get('import', '')}`\n"
        f"- Callable: `{output.get('callable', '')}`\n"
        f"- Signature: `{output.get('signature', '')}`\n"
        "- Implementation scope: use **Source entrypoints** above to locate code in `repo/`; "
        "the import line lists the public surface your package must expose.\n\n"
        "## Constraints\n\n"
        "- The final answer must be files under `submission/`.\n"
        "- Do not modify `repo/` or `public_tests/` as your final deliverable.\n"
        "- Do not import from the original source package or rely on the original repo path at runtime.\n"
        "- Do not symlink or copy hidden/evaluator files. They are intentionally unavailable.\n"
        "- Keep only behavior-relevant code and dependencies needed for the target feature; "
        "prefer a compact closure, but do not remove helpers/resources required by edge cases.\n"
        "- **Forbidden imports are a hard gate:** if your submission imports a forbidden name, "
        "`functional_gate` is 0 even when tests pass.\n"
        "- **Scoring:** `final_score = functional_gate × (1 - extraction_ratio)`. "
        "Passing with a whole-repo copy scores near zero — extract only what the feature needs.\n"
        f"- Allowed dependencies:\n{allowed_dependencies}\n"
        f"- Forbidden dependencies:\n{forbidden_dependencies}\n"
        f"- Forbidden imports:\n{forbidden_imports}\n\n"
        "You may run the public tests during development. The evaluator will later run public and "
        "hidden tests in a clean environment. When finished, run:\n\n"
        "```bash\n"
        "echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT\n"
        "```\n"
    )


def _copy_path(src: Path, dst: Path) -> None:
    ignore = shutil.ignore_patterns(
        "__pycache__",
        "*.pyc",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".git",
    )
    if src.is_dir():
        shutil.copytree(src, dst, ignore=ignore, dirs_exist_ok=True)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def _copy_submission(src: Path, dst: Path) -> None:
    _reset_dir(dst)
    shutil.copytree(src, dst, dirs_exist_ok=True)


def _reset_dir(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def _has_submission_files(path: Path) -> bool:
    if not path.is_dir():
        return False
    return any(child.name != ".gitkeep" for child in path.iterdir())


def _package_has_python_files(path: Path) -> bool:
    return path.is_dir() and any(path.rglob("*.py"))


def _recover_misplaced_submission(workspace_dir: Path, submission_dir: Path) -> dict[str, Any] | None:
    """Collect agent output from known misplaced workspace paths into submission/."""

    if _has_submission_files(submission_dir):
        return None

    recovery_sources: list[str] = []
    try:
        featurelifted_root = workspace_dir / "featurelifted"
        if _package_has_python_files(featurelifted_root):
            dest = submission_dir / "featurelifted"
            submission_dir.mkdir(parents=True, exist_ok=True)
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(featurelifted_root, dest, dirs_exist_ok=True)
            recovery_sources.append("workspace/featurelifted")

        pyproject_root = workspace_dir / "pyproject.toml"
        if pyproject_root.is_file() and not (submission_dir / "pyproject.toml").is_file():
            submission_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(pyproject_root, submission_dir / "pyproject.toml")
            recovery_sources.append("workspace/pyproject.toml")
    except OSError as exc:
        return {
            "recovered": False,
            "recovery_sources": recovery_sources,
            "message": f"submission recovery failed: {exc}",
        }

    if not recovery_sources or not _has_submission_files(submission_dir):
        return None

    sources_text = ", ".join(recovery_sources)
    return {
        "recovered": True,
        "recovery_sources": recovery_sources,
        "message": (
            f"recovered submission from misplaced paths ({sources_text}); "
            "agent wrote outside workspace/submission"
        ),
    }


def _missing_submission_diagnostic(workspace_dir: Path) -> str:
    if _package_has_python_files(workspace_dir / "featurelifted"):
        return (
            "workspace/featurelifted exists but submission recovery did not populate "
            "workspace/submission"
        )
    return "no submission files and no recoverable misplaced paths found under workspace/"


def _write_agent_logs(agent_output_dir: Path, result: Any) -> None:
    agent_output_dir.mkdir(parents=True, exist_ok=True)
    (agent_output_dir / "stdout.log").write_text(result.stdout, encoding="utf-8")
    (agent_output_dir / "stderr.log").write_text(result.stderr, encoding="utf-8")


def _collect_agent_usage(agent_name: str, agent_output_dir: Path) -> dict[str, Any]:
    """Collect token and step usage without making usage availability affect grading."""

    usage_path = agent_output_dir / "usage.json"
    if usage_path.is_file():
        return _parse_agent_usage_json(usage_path)

    normalized = agent_name.strip().lower().replace("_", "-")
    if normalized in {"mini", "mini-swe-agent", "minisweagent"}:
        return _parse_mini_trajectory_usage(agent_output_dir / "trajectory.json")

    return _unavailable_agent_usage(usage_path, "usage.json not found")


def _parse_agent_usage_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return _unavailable_agent_usage(path, f"cannot read usage.json: {exc}")
    except json.JSONDecodeError as exc:
        return _unavailable_agent_usage(path, f"invalid usage.json: {exc}")
    if not isinstance(data, dict):
        return _unavailable_agent_usage(path, "usage.json must contain a JSON object")
    return _sanitize_usage_payload(data, path)


def _aggregate_message_usage(messages: list[Any]) -> dict[str, int]:
    prompt_tokens = 0
    completion_tokens = 0
    total_tokens = 0
    saw_prompt = False
    saw_completion = False
    saw_total = False

    for message in messages:
        if not isinstance(message, dict):
            continue
        extra = message.get("extra")
        if not isinstance(extra, dict):
            continue
        response = extra.get("response")
        if not isinstance(response, dict):
            continue
        usage = response.get("usage")
        if not isinstance(usage, dict):
            continue

        prompt = _int_metric(usage.get("prompt_tokens"))
        if prompt is not None:
            prompt_tokens += prompt
            saw_prompt = True
        completion = _int_metric(usage.get("completion_tokens"))
        if completion is not None:
            completion_tokens += completion
            saw_completion = True
        total = _int_metric(usage.get("total_tokens"))
        if total is not None:
            total_tokens += total
            saw_total = True

    aggregated: dict[str, int] = {}
    if saw_prompt:
        aggregated["prompt_tokens"] = prompt_tokens
    if saw_completion:
        aggregated["completion_tokens"] = completion_tokens
    if saw_prompt or saw_completion:
        aggregated["total_tokens"] = prompt_tokens + completion_tokens
    elif saw_total:
        aggregated["total_tokens"] = total_tokens
    return aggregated


def _parse_mini_trajectory_usage(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return _unavailable_agent_usage(path, "trajectory.json not found")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return _unavailable_agent_usage(path, f"cannot read trajectory.json: {exc}")
    except json.JSONDecodeError as exc:
        return _unavailable_agent_usage(path, f"invalid trajectory.json: {exc}")
    if not isinstance(data, dict):
        return _unavailable_agent_usage(path, "trajectory.json must contain a JSON object")

    info = data.get("info") if isinstance(data.get("info"), dict) else {}
    model_stats = info.get("model_stats") if isinstance(info.get("model_stats"), dict) else {}
    messages = data.get("messages")

    usage: dict[str, Any] = {"available": True, "source": str(path)}
    if isinstance(messages, list):
        usage["total_messages"] = len(messages)
        usage["assistant_steps"] = sum(
            1
            for message in messages
            if isinstance(message, dict) and message.get("role") == "assistant"
        )

    for key in (
        "api_calls",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "trace_tokens",
        "billed_tokens",
    ):
        value = _int_metric(model_stats.get(key))
        if value is not None:
            usage[key] = value

    if isinstance(messages, list):
        aggregated = _aggregate_message_usage(messages)
        for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
            if key not in usage and key in aggregated:
                usage[key] = aggregated[key]

    exit_status = info.get("exit_status")
    if isinstance(exit_status, str):
        usage["exit_status"] = exit_status
    if len(usage) <= 2:
        return _unavailable_agent_usage(path, "trajectory.json did not contain usage metrics")
    return usage


def _sanitize_usage_payload(data: dict[str, Any], source: Path) -> dict[str, Any]:
    usage: dict[str, Any] = {"available": True, "source": str(source)}
    for key in USAGE_SUM_FIELDS:
        value = _int_metric(data.get(key))
        if value is not None:
            usage[key] = value
    exit_status = data.get("exit_status")
    if isinstance(exit_status, str):
        usage["exit_status"] = exit_status
    if len(usage) <= 2:
        return _unavailable_agent_usage(source, "usage.json did not contain usage metrics")
    return usage


def _sum_agent_usage(runs: list[dict[str, Any]]) -> dict[str, Any]:
    usages: list[dict[str, Any]] = []
    for run in runs:
        agent = run.get("agent") if isinstance(run.get("agent"), dict) else {}
        usage = agent.get("usage") if isinstance(agent.get("usage"), dict) else {}
        if usage.get("available") is True:
            usages.append(usage)

    totals: dict[str, Any] = {
        "available_runs": len(usages),
        "missing_runs": len(runs) - len(usages),
    }
    for key in USAGE_SUM_FIELDS:
        totals[key] = sum(
            value for usage in usages if isinstance((value := usage.get(key)), int)
        )
    return totals


def _unavailable_agent_usage(source: Path, reason: str) -> dict[str, Any]:
    return {
        "available": False,
        "source": str(source),
        "reason": reason,
    }


def _int_metric(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def _test_path(metadata: dict[str, Any], key: str, default: str) -> str:
    tests = metadata.get("tests")
    if isinstance(tests, dict):
        value = tests.get(key)
        if isinstance(value, str) and value:
            return value
    return default


def _dependency_lock(metadata: dict[str, Any]) -> str:
    environment = metadata.get("environment")
    if isinstance(environment, dict):
        value = environment.get("dependency_lock")
        if isinstance(value, str) and value:
            return value
    return "requirements.lock"


def _format_list(value: Any) -> str:
    if not isinstance(value, list) or not value:
        return "- None"
    return "\n".join(f"- {item}" for item in value if isinstance(item, str))


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
