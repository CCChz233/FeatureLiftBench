#!/usr/bin/env python3
"""Validate that an OpenHands smoke-first run reached the LLM and Docker eval."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


BAD_EXIT_STATUSES = {
    "timeout",
    "log_limit_exceeded",
    "openhands_failed",
    "command_not_found",
    "not_configured",
    "invalid_command_template",
    "step_limit_exceeded",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _run_json_path(path: Path) -> Path:
    if path.is_file():
        return path
    direct = path / "run.json"
    if direct.is_file():
        return direct
    candidates = sorted(path.glob("*/run.json"))
    if candidates:
        return candidates[0]
    raise FileNotFoundError(f"missing run.json under {path}")


def check(path: Path) -> list[str]:
    errors: list[str] = []
    run_path = _run_json_path(path)
    run = _load_json(run_path)
    agent = run.get("agent") if isinstance(run.get("agent"), dict) else {}
    usage = agent.get("usage") if isinstance(agent.get("usage"), dict) else {}
    evaluation = run.get("evaluation") if isinstance(run.get("evaluation"), dict) else {}

    api_calls = usage.get("api_calls")
    if not isinstance(api_calls, int) or api_calls < 1:
        errors.append("agent usage api_calls must be >= 1")

    exit_status = usage.get("exit_status")
    if isinstance(exit_status, str) and exit_status in BAD_EXIT_STATUSES:
        errors.append(f"bad OpenHands exit_status: {exit_status}")

    if evaluation.get("docker_sandbox_error") is True:
        errors.append("evaluation docker_sandbox_error=true")

    return errors


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        print("usage: check_openhands_smoke.py <smoke-output-or-run.json>", file=sys.stderr)
        return 2
    path = Path(args[0]).resolve()
    try:
        errors = check(path)
    except (OSError, json.JSONDecodeError, FileNotFoundError) as exc:
        print(f"smoke-first check failed: {exc}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"smoke-first check failed: {error}", file=sys.stderr)
        return 1
    print(f"smoke-first check ok: {path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
