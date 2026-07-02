"""Command line interface for FeatureLiftBench."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .agent_adapters import SUPPORTED_AGENTS
from .agent_docker import DEFAULT_AGENT_IMAGE
from .docker_eval import DEFAULT_EVAL_IMAGE
from .docker_eval import DEFAULT_GO_EVAL_IMAGE
from .docker_eval import evaluate_submission_docker
from .evaluator import evaluate_submission
from .paths import DEFAULT_AGENT_CONFIG
from .paths import DEFAULT_LOCAL_CONFIG
from .paths import resolve_task_input
from .validate import validate_task


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="featureliftbench")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate-task", help="validate a task directory")
    validate_parser.add_argument("task_dir", type=Path)
    validate_parser.add_argument("--json", action="store_true", help="print machine-readable output")

    eval_parser = subparsers.add_parser("eval", help="evaluate a submission")
    eval_parser.add_argument("task_dir", type=Path)
    eval_parser.add_argument("submission_dir", type=Path)
    eval_parser.add_argument("--output", type=Path, required=True)
    eval_parser.add_argument(
        "--docker",
        action="store_true",
        help="run evaluation inside the featureliftbench-eval Docker image",
    )
    eval_parser.add_argument(
        "--docker-image",
        default=DEFAULT_EVAL_IMAGE,
        help=(
            f"Docker image for --docker "
            f"(default: {DEFAULT_EVAL_IMAGE}; Go tasks auto-use {DEFAULT_GO_EVAL_IMAGE})"
        ),
    )

    score_parser = subparsers.add_parser("score", help="print scores from a result file")
    score_parser.add_argument("result_json", type=Path)

    run_agent_parser = subparsers.add_parser(
        "run-agent",
        help="run an agent on one task directory or every task under a dataset root",
    )
    run_agent_parser.add_argument("input_path", type=Path)
    run_agent_parser.add_argument("--output", type=Path, required=True)
    run_agent_parser.add_argument(
        "--agent",
        default="mini-swe-agent",
        help=f"agent adapter to use; supported: {', '.join(SUPPORTED_AGENTS)}",
    )
    run_agent_parser.add_argument("--agent-bin", help="agent executable; defaults to adapter default")
    run_agent_parser.add_argument("--model", help="model name passed to the agent")
    run_agent_parser.add_argument("--config", help="agent config file path")
    run_agent_parser.add_argument(
        "--agent-config",
        type=Path,
        default=DEFAULT_AGENT_CONFIG,
        help="FeatureLiftBench agent TOML config file with profiles and model settings",
    )
    run_agent_parser.add_argument(
        "--agent-profile",
        help="profile name in --agent-config; defaults to config profile or 'default'",
    )
    run_agent_parser.add_argument(
        "--env-file",
        type=Path,
        help="dotenv-style file containing secrets such as FEATURELIFTBENCH_API_KEY",
    )
    run_agent_parser.add_argument("--yolo", action="store_true", help="pass --yolo to mini-swe-agent")
    run_agent_parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=3600,
        help="maximum wall-clock seconds for each agent task run",
    )
    run_agent_parser.add_argument(
        "--num-workers",
        type=int,
        default=1,
        help="number of task runs to execute concurrently when input_path is a dataset root",
    )
    run_agent_parser.add_argument(
        "--agent-command",
        help=(
            "command template. --agent command placeholders: {workspace}, {task_file}, "
            "{submission_dir}, {agent_output_dir}. --agent openhands-agent additionally "
            "supports: {prompt_file}, {model}, {python}"
        ),
    )
    run_agent_parser.add_argument(
        "--no-progress",
        action="store_true",
        help="disable live suite progress UI and print plain started/finished lines instead",
    )
    run_agent_parser.add_argument(
        "--agent-arg",
        action="append",
        default=[],
        help="extra argument appended to the agent command; may be repeated",
    )
    run_agent_parser.add_argument(
        "--task-id",
        action="append",
        dest="task_ids",
        help="limit suite run to specific task_id values; may be repeated",
    )
    run_agent_parser.add_argument(
        "--skip-completed",
        type=Path,
        help="deprecated alias: previous suite output directory; retains only passed tasks",
    )
    run_agent_parser.add_argument(
        "--resume",
        nargs="?",
        const=True,
        default=None,
        metavar="DIR",
        help="resume a suite run in --output (or DIR); retains non-retry statuses from existing suite.json",
    )
    run_agent_parser.add_argument(
        "--retry-only-status",
        default=None,
        help=(
            "comma-separated run statuses to re-run when using --resume "
            "(default: missing_submission,failed,not_evaluated)"
        ),
    )
    run_agent_parser.add_argument(
        "--extra-agent-passes",
        type=int,
        default=0,
        help="after the first suite pass, automatically re-run failed tasks up to N additional times",
    )
    run_agent_parser.add_argument(
        "--max-task-attempts",
        type=int,
        default=None,
        help="skip agent re-runs for tasks that already reached this many attempts",
    )
    run_agent_parser.add_argument(
        "--retry-rate-limit",
        type=int,
        default=1,
        help=(
            "when a task fails due to API rate limiting, retry up to this many total attempts "
            "(waits ~65s between tries to clear TPM windows; default: 1)"
        ),
    )
    run_agent_parser.add_argument(
        "--eval-docker",
        action="store_true",
        help="evaluate collected submissions inside the Docker eval image",
    )
    run_agent_parser.add_argument(
        "--eval-docker-image",
        default=DEFAULT_EVAL_IMAGE,
        help=(
            f"Docker image for --eval-docker "
            f"(default: {DEFAULT_EVAL_IMAGE}; Go tasks auto-use {DEFAULT_GO_EVAL_IMAGE})"
        ),
    )
    run_agent_parser.add_argument(
        "--agent-docker",
        action="store_true",
        help="run the agent itself inside the FeatureLiftBench agent Docker image",
    )
    run_agent_parser.add_argument(
        "--agent-docker-image",
        default=None,
        help=f"Docker image for --agent-docker (default: {DEFAULT_AGENT_IMAGE})",
    )

    setup_parser = subparsers.add_parser(
        "setup",
        help="validate flb.local.toml, Docker images, and LLM connectivity",
    )
    setup_parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_LOCAL_CONFIG,
        help="local experiment config (default: flb.local.toml)",
    )
    setup_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print resolved runtime policy without running checks",
    )

    run_parser = subparsers.add_parser(
        "run",
        help="run a suite from flb.local.toml (preflight, agent, eval, analysis)",
    )
    run_parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_LOCAL_CONFIG,
        help="local experiment config (default: flb.local.toml)",
    )
    run_parser.add_argument(
        "--suite",
        choices=["sanity", "smoke", "pilot5", "main", "custom"],
        help="override [run].suite from config",
    )
    run_parser.add_argument("--max-steps", type=int, help="override [agent].max_steps")
    run_parser.add_argument("--workers", type=int, help="override [run].workers")
    run_parser.add_argument("--output", type=Path, help="override output directory")
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print resolved plan without running",
    )

    resume_parser = subparsers.add_parser(
        "resume",
        help="resume a previous featureliftbench run output directory",
    )
    resume_parser.add_argument("output_dir", type=Path)
    resume_parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_LOCAL_CONFIG,
        help="local experiment config (default: flb.local.toml)",
    )
    resume_parser.add_argument(
        "--suite",
        choices=["sanity", "smoke", "pilot5", "main", "custom"],
        help="override [run].suite from config",
    )
    resume_parser.add_argument("--max-steps", type=int, help="override [agent].max_steps")
    resume_parser.add_argument("--workers", type=int, help="override [run].workers")
    resume_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print resolved plan without running",
    )

    smoke_parser = subparsers.add_parser(
        "smoke",
        help="run smoke suite (1-task OpenHands + eval gate)",
    )
    smoke_parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_LOCAL_CONFIG,
        help="local experiment config (default: flb.local.toml)",
    )
    smoke_parser.add_argument("--max-steps", type=int, help="override [agent].max_steps")
    smoke_parser.add_argument("--workers", type=int, help="override [run].workers")
    smoke_parser.add_argument("--output", type=Path, help="override output directory")
    smoke_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print resolved plan without running",
    )

    args = parser.parse_args(argv)

    if args.command == "validate-task":
        return _cmd_validate_task(args)
    if args.command == "eval":
        return _cmd_eval(args)
    if args.command == "score":
        return _cmd_score(args)
    if args.command == "run-agent":
        return _cmd_run_agent(args)
    if args.command == "setup":
        return _cmd_setup(args)
    if args.command == "run":
        return _cmd_run(args)
    if args.command == "resume":
        return _cmd_resume(args)
    if args.command == "smoke":
        return _cmd_smoke(args)

    parser.error(f"unknown command: {args.command}")
    return 2


def _cmd_validate_task(args: argparse.Namespace) -> int:
    result = validate_task(args.task_dir)

    if args.json:
        payload = {
            "task_dir": str(result.task_dir),
            "task_id": result.task_id,
            "valid": result.valid,
            "errors": result.errors,
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif result.valid:
        print(f"valid task: {result.task_id}")
    else:
        print(f"invalid task: {args.task_dir}", file=sys.stderr)
        for error in result.errors:
            print(f"- {error}", file=sys.stderr)

    return 0 if result.valid else 1


def _cmd_eval(args: argparse.Namespace) -> int:
    use_docker = args.docker or os.environ.get("FEATURELIFTBENCH_EVAL_DOCKER", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }
    if use_docker:
        result = evaluate_submission_docker(
            args.task_dir,
            args.submission_dir,
            args.output,
            image=args.docker_image,
            use_docker=True,
        )
    else:
        result = evaluate_submission(args.task_dir, args.submission_dir, args.output)
    result_path = args.output / "result.json"
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"wrote result: {result_path}", file=sys.stderr)
    return 0 if result["status"] == "passed" else 1


def _cmd_score(args: argparse.Namespace) -> int:
    try:
        data = json.loads(args.result_json.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"cannot read result file: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"invalid result JSON: {exc}", file=sys.stderr)
        return 1

    scores = data.get("scores")
    if not isinstance(scores, dict):
        print("result JSON does not contain scores", file=sys.stderr)
        return 1

    print(json.dumps(scores, indent=2, sort_keys=True))
    return 0


def _cmd_run_agent(args: argparse.Namespace) -> int:
    from .agent_adapters import AgentRunConfig
    from .agent_config import load_agent_run_config
    from .agent_runner import run_agent_on_path
    from .suite_utils import parse_retry_only_statuses

    base_config = AgentRunConfig(
        agent=args.agent,
        agent_bin=args.agent_bin,
        model=args.model,
        config=args.config,
        yolo=args.yolo,
        timeout_seconds=args.timeout_seconds,
        command=args.agent_command,
        extra_args=tuple(args.agent_arg or []),
    )
    try:
        loaded_config = load_agent_run_config(
            base_config=base_config,
            config_path=args.agent_config,
            profile_name=args.agent_profile,
            env_file=args.env_file,
        )
        resume_dir, resume_mode = _resolve_resume_args(args)
        retry_only_statuses = parse_retry_only_statuses(args.retry_only_status)
        eval_docker = args.eval_docker or _env_truthy("FEATURELIFTBENCH_EVAL_DOCKER")
        agent_docker = args.agent_docker or _env_truthy("FEATURELIFTBENCH_AGENT_DOCKER")
        agent_docker_image = (
            args.agent_docker_image
            or os.environ.get("FEATURELIFTBENCH_AGENT_DOCKER_IMAGE", "").strip()
            or DEFAULT_AGENT_IMAGE
        )
        result = run_agent_on_path(
            resolve_task_input(args.input_path),
            args.output,
            loaded_config.run_config,
            agent_config_summary=loaded_config.summary,
            num_workers=args.num_workers,
            progress=not args.no_progress,
            task_ids=args.task_ids or None,
            skip_completed_dir=args.skip_completed,
            retry_rate_limit=args.retry_rate_limit,
            resume_dir=resume_dir,
            resume_mode=resume_mode,
            retry_only_statuses=retry_only_statuses,
            extra_agent_passes=args.extra_agent_passes,
            max_task_attempts=args.max_task_attempts,
            eval_docker=eval_docker,
            eval_docker_image=args.eval_docker_image,
            agent_docker=agent_docker,
            agent_docker_image=agent_docker_image,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2, sort_keys=True))
    if result.get("mode") == "suite":
        return 0 if result.get("summary", {}).get("failed") == 0 else 1
    return 0 if result.get("status") == "passed" else 1


def _env_truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes"}


def _resolve_resume_args(args: argparse.Namespace) -> tuple[Path | None, bool]:
    if args.resume is not None:
        if args.resume is True:
            return args.output.resolve(), True
        return Path(args.resume).resolve(), True
    return None, False


def _cmd_setup(args: argparse.Namespace) -> int:
    from .run_workflow import cmd_setup

    try:
        return cmd_setup(config_path=args.config, dry_run=args.dry_run)
    except (ValueError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


def _cmd_run(args: argparse.Namespace) -> int:
    from .run_workflow import cmd_run

    try:
        result = cmd_run(
            config_path=args.config,
            suite=args.suite,
            max_steps=args.max_steps,
            workers=args.workers,
            output_dir=str(args.output) if args.output else None,
            dry_run=args.dry_run,
        )
    except (ValueError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not result.dry_run:
        print(f"Done: {result.output_dir}", file=sys.stderr)
    return result.exit_code


def _cmd_resume(args: argparse.Namespace) -> int:
    from .run_workflow import cmd_run

    try:
        result = cmd_run(
            config_path=args.config,
            resume_dir=args.output_dir.resolve(),
            suite=args.suite,
            max_steps=args.max_steps,
            workers=args.workers,
            dry_run=args.dry_run,
        )
    except (ValueError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not result.dry_run:
        print(f"Done: {result.output_dir}", file=sys.stderr)
    return result.exit_code


def _cmd_smoke(args: argparse.Namespace) -> int:
    from .run_workflow import cmd_run

    try:
        result = cmd_run(
            config_path=args.config,
            suite="smoke",
            max_steps=args.max_steps,
            workers=args.workers,
            output_dir=str(args.output) if args.output else None,
            dry_run=args.dry_run,
        )
    except (ValueError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not result.dry_run:
        print(f"Done: {result.output_dir}", file=sys.stderr)
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
