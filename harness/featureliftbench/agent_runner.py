"""Agent workspace preparation and end-to-end run orchestration."""

from __future__ import annotations

import json
import shutil
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from datetime import UTC
from datetime import datetime
from pathlib import Path
from typing import Any

from .agent_adapters import AgentRunConfig
from .agent_adapters import AgentRunContext
from .agent_adapters import get_agent_adapter
from .evaluator import evaluate_submission
from .metadata import load_metadata
from .paths import resolve_task_input
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

USAGE_COMPACT_FIELDS = (
    "assistant_steps",
    "api_calls",
    "prompt_tokens",
    "completion_tokens",
    "total_tokens",
)


def run_agent_on_path(
    input_path: str | Path,
    output_dir: str | Path,
    config: AgentRunConfig,
    agent_config_summary: dict[str, Any] | None = None,
    num_workers: int = 1,
    progress: bool = False,
) -> dict[str, Any]:
    """Run an agent on one task directory or every task under a dataset root."""

    resolved = resolve_task_input(input_path)
    task_dirs = discover_task_dirs(resolved)
    output_path = Path(output_dir).resolve()
    if len(task_dirs) == 1 and (resolved / "metadata.json").is_file():
        return run_agent_on_task(
            task_dirs[0],
            output_path,
            config,
            agent_config_summary=agent_config_summary,
        )
    return run_agent_on_suite(
        task_dirs,
        output_path,
        config,
        agent_config_summary=agent_config_summary,
        num_workers=num_workers,
        progress=progress,
    )


def run_agent_on_suite(
    task_dirs: list[Path],
    output_dir: str | Path,
    config: AgentRunConfig,
    agent_config_summary: dict[str, Any] | None = None,
    num_workers: int = 1,
    progress: bool = False,
) -> dict[str, Any]:
    """Run an agent on multiple tasks and write a suite summary."""

    output_path = Path(output_dir).resolve()
    output_path.mkdir(parents=True, exist_ok=True)
    worker_count = max(1, int(num_workers))

    runs = _run_suite_tasks(
        task_dirs=task_dirs,
        output_path=output_path,
        config=config,
        agent_config_summary=agent_config_summary,
        num_workers=worker_count,
        progress=progress,
    )

    final_scores = [
        run.get("evaluation", {}).get("scores", {}).get("final_score")
        for run in runs
        if isinstance(run.get("evaluation"), dict)
    ]
    numeric_scores = [score for score in final_scores if isinstance(score, (int, float))]
    agent_usage_totals = _sum_agent_usage(runs)
    summary = {
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
    result = {
        "mode": "suite",
        "generated_at": _utc_now(),
        "agent": config.agent,
        "agent_config": agent_config_summary or {},
        "output_dir": str(output_path),
        "num_workers": worker_count,
        "summary": summary,
        "agent_usage_totals": agent_usage_totals,
        "runs": [
            {
                "task_id": run.get("task_id", ""),
                "status": run.get("status", "failed"),
                "run_json": run.get("run_json", ""),
                "result_json": run.get("evaluation", {}).get("result_json", ""),
                "final_score": run.get("evaluation", {}).get("scores", {}).get("final_score", 0.0),
                "agent_usage": _compact_agent_usage(
                    run.get("agent", {}).get("usage", {})
                    if isinstance(run.get("agent"), dict)
                    else {}
                ),
            }
            for run in runs
        ],
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
) -> dict[str, Any]:
    """Run an agent on a single task, collect its submission, and evaluate it."""

    task_path = Path(task_dir).resolve()
    output_path = Path(output_dir).resolve()
    output_path.mkdir(parents=True, exist_ok=True)

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

    agent_result = None
    eval_result = None
    workspace_submission_dir = workspace_dir / "submission"

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
        adapter = get_agent_adapter(config.agent)
        stdout_log = agent_output_dir / "stdout.log"
        stderr_log = agent_output_dir / "stderr.log"
        try:
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
            eval_result = evaluate_submission(task_path, collected_submission_dir, eval_output_dir)
        else:
            errors.append("agent did not create any files under workspace/submission")

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
    result = {
        "mode": "task",
        "generated_at": _utc_now(),
        "task_id": task_id,
        "status": status,
        "agent": agent_payload,
        "agent_config": agent_config_summary or {},
        "workspace": {
            "dir": str(workspace_dir),
            "task_file": str(workspace_dir / "TASK.md"),
        },
        "submission": {
            "dir": str(collected_submission_dir),
            "exists": submission_exists,
        },
        "evaluation": evaluation_payload,
        "errors": errors,
        "run_json": str(run_json_path),
    }
    run_json_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result


def _run_suite_tasks(
    *,
    task_dirs: list[Path],
    output_path: Path,
    config: AgentRunConfig,
    agent_config_summary: dict[str, Any] | None,
    num_workers: int,
    progress: bool,
) -> list[dict[str, Any]]:
    total = len(task_dirs)
    use_live_progress = progress and sys.stderr.isatty() and total > 1

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
) -> list[dict[str, Any]]:
    if num_workers == 1:
        runs = []
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
                )
            )
        return runs

    runs_by_index: dict[int, dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
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
            ): index
            for index, task_dir in enumerate(task_dirs, start=1)
        }
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
                )
    return [runs_by_index[index] for index in range(1, total + 1)]


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
) -> dict[str, Any]:
    task_id = task_dir.name
    if progress_manager is not None:
        progress_manager.on_task_start(task_id)
        progress_manager.update_task_status(task_id, "preparing workspace")
    else:
        _progress(progress, f"[{index}/{total}] started {task_id}")

    run_output = output_path / task_id
    try:
        result = run_agent_on_task(
            task_dir,
            run_output,
            config,
            agent_config_summary=agent_config_summary,
        )
    except Exception as exc:  # Defensive: one task should not abort the suite.
        result = _exception_run_result(
            task_dir,
            run_output,
            config,
            agent_config_summary,
            exc,
            progress_manager=progress_manager,
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
            "usage": _unavailable_agent_usage(output_dir / "agent" / "usage.json", "task raised before usage was available"),
        },
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


def discover_task_dirs(input_path: str | Path) -> list[Path]:
    """Discover task directories from either a task dir or a dataset root."""

    path = resolve_task_input(input_path)
    if (path / "metadata.json").is_file():
        return [path]
    if not path.is_dir():
        raise ValueError(f"task path does not exist or is not a directory: {path}")
    skip_dirs = {"extreme"}
    task_dirs = sorted(
        child
        for child in path.iterdir()
        if child.name not in skip_dirs and (child / "metadata.json").is_file()
    )
    if not task_dirs:
        raise ValueError(f"no task directories found under: {path}")
    return task_dirs


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

    return (
        f"# FeatureLiftBench Task: {metadata.get('task_id', '')}\n\n"
        "You are in a FeatureLiftBench agent workspace. Decouple the requested feature from "
        "`repo/` into a standalone, installable Python package under `submission/`.\n\n"
        "## Workspace\n\n"
        "- `repo/`: source repository snapshot for the fixed commit.\n"
        "- `public_tests/`: tests you may run while developing.\n"
        "- `requirements.lock`: locked third-party runtime dependencies allowed by the task.\n"
        "- `metadata.json`: redacted task metadata. Hidden tests and evaluator internals are not present.\n"
        "- `submission/`: write your final package here.\n\n"
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
        f"- Signature: `{output.get('signature', '')}`\n\n"
        "## Constraints\n\n"
        "- The final answer must be files under `submission/`.\n"
        "- Do not modify `repo/` or `public_tests/` as your final deliverable.\n"
        "- Do not import from the original source package or rely on the original repo path at runtime.\n"
        "- Do not symlink or copy hidden/evaluator files. They are intentionally unavailable.\n"
        "- Keep only code and dependencies needed for the target feature.\n"
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


def _compact_agent_usage(usage: dict[str, Any]) -> dict[str, Any]:
    if usage.get("available") is not True:
        compact = {
            "available": False,
            "reason": usage.get("reason", "usage unavailable"),
        }
        if isinstance(usage.get("source"), str):
            compact["source"] = usage["source"]
        return compact

    compact: dict[str, Any] = {"available": True}
    for key in USAGE_COMPACT_FIELDS:
        value = usage.get(key)
        if isinstance(value, int):
            compact[key] = value
    return compact


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


def _evaluation_payload(eval_result: dict[str, Any] | None, eval_output_dir: Path) -> dict[str, Any]:
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
    }


def _run_status(
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
