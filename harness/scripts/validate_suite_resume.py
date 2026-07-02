#!/usr/bin/env python3
"""Validate a suite output directory before resuming a run."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "harness"))


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object: {path}")
    return data


def validate_suite_resume(
    suite_dir: Path,
    *,
    require_docker_eval: bool = False,
) -> list[str]:
    """Return human-readable validation errors; empty list means resume is safe."""

    suite_dir = suite_dir.resolve()
    errors: list[str] = []

    if not suite_dir.is_dir():
        return [f"suite directory not found: {suite_dir}"]

    suite_path = suite_dir / "suite.json"
    if not suite_path.is_file():
        errors.append(f"missing suite.json: {suite_path}")
        return errors

    suite = _load_json(suite_path)
    runs = suite.get("runs")
    if not isinstance(runs, list) or not runs:
        errors.append("suite.json has no runs to resume from")
        return errors

    for run in runs:
        if not isinstance(run, dict):
            errors.append("suite.json contains a non-object run entry")
            continue
        task_id = run.get("task_id")
        if not isinstance(task_id, str) or not task_id:
            errors.append("suite.json run entry missing task_id")
            continue

        task_dir = suite_dir / task_id
        run_json_path = Path(run.get("run_json") or task_dir / "run.json")
        usage_json_path = task_dir / "agent" / "usage.json"
        submission_dir = task_dir / "submission"
        eval_result_path = task_dir / "eval" / "result.json"

        if not run_json_path.is_file():
            errors.append(f"{task_id}: missing run.json ({run_json_path})")
        if not usage_json_path.is_file():
            errors.append(f"{task_id}: missing agent/usage.json")
        if not submission_dir.is_dir():
            errors.append(f"{task_id}: missing submission/ directory")

        detail: dict[str, Any] = {}
        if run_json_path.is_file():
            try:
                detail = _load_json(run_json_path)
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                errors.append(f"{task_id}: unreadable run.json: {exc}")
                detail = {}

        usage: dict[str, Any] = {}
        if usage_json_path.is_file():
            try:
                usage_payload = _load_json(usage_json_path)
                if isinstance(usage_payload, dict):
                    usage = usage_payload
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                errors.append(f"{task_id}: unreadable agent/usage.json: {exc}")

        agent = detail.get("agent") if isinstance(detail.get("agent"), dict) else {}
        detail_usage = agent.get("usage") if isinstance(agent.get("usage"), dict) else {}
        api_calls = detail_usage.get("api_calls", usage.get("api_calls"))
        assistant_steps = detail_usage.get("assistant_steps", usage.get("assistant_steps"))
        if isinstance(api_calls, int) and api_calls > 0:
            if not isinstance(assistant_steps, int) or assistant_steps <= 0:
                errors.append(
                    f"{task_id}: api_calls={api_calls} but assistant_steps={assistant_steps!r}; "
                    "likely stale or corrupted run data"
                )

        status = run.get("status")
        if status == "passed" and isinstance(api_calls, int) and api_calls <= 0:
            errors.append(
                f"{task_id}: status=passed with api_calls={api_calls}; "
                "remove or rerun this task before resume"
            )

        if require_docker_eval:
            if not eval_result_path.is_file():
                errors.append(f"{task_id}: missing eval/result.json (docker suite resume)")
                continue
            try:
                eval_result = _load_json(eval_result_path)
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                errors.append(f"{task_id}: unreadable eval/result.json: {exc}")
                continue
            sandbox = eval_result.get("sandbox")
            backend = sandbox.get("backend") if isinstance(sandbox, dict) else None
            if backend != "docker":
                errors.append(
                    f"{task_id}: eval sandbox.backend={backend!r}; expected 'docker' for formal suite resume"
                )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("suite_dir", type=Path, help="Suite output directory to validate")
    parser.add_argument(
        "--require-docker-eval",
        action="store_true",
        help="Require eval/result.json with sandbox.backend=docker for every completed task",
    )
    args = parser.parse_args(argv)

    errors = validate_suite_resume(
        args.suite_dir,
        require_docker_eval=args.require_docker_eval,
    )
    if errors:
        print("validate_suite_resume: resume blocked:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        print(
            "Fix corrupted task directories or rerun affected tasks before resume.",
            file=sys.stderr,
        )
        return 1

    print(f"validate_suite_resume: ok ({args.suite_dir.resolve()})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
