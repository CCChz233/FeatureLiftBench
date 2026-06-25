"""Command line interface for FeatureLiftBench."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .agent_adapters import SUPPORTED_AGENTS
from .docker_eval import DEFAULT_EVAL_IMAGE
from .docker_eval import evaluate_submission_docker
from .evaluator import evaluate_submission
from .paths import DEFAULT_AGENT_CONFIG
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
        help=f"Docker image for --docker (default: {DEFAULT_EVAL_IMAGE})",
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
            "command template for --agent command; placeholders: "
            "{workspace}, {task_file}, {submission_dir}, {agent_output_dir}"
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
        help="previous suite output directory; skip agent runs for tasks that already passed",
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

    args = parser.parse_args(argv)

    if args.command == "validate-task":
        return _cmd_validate_task(args)
    if args.command == "eval":
        return _cmd_eval(args)
    if args.command == "score":
        return _cmd_score(args)
    if args.command == "run-agent":
        return _cmd_run_agent(args)

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
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2, sort_keys=True))
    if result.get("mode") == "suite":
        return 0 if result.get("summary", {}).get("failed") == 0 else 1
    return 0 if result.get("status") == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
