#!/usr/bin/env python3
"""Merge OpenHands pilot suite shards into an explicit pilot summary."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "harness"))

from featureliftbench.agent_runner import _sum_agent_usage  # noqa: E402
from featureliftbench.suite_utils import compact_suite_run_entry  # noqa: E402
from featureliftbench.suite_utils import rebuild_suite_summary  # noqa: E402


def merge_pilot_suites(output_dir: Path, suite_dirs: list[Path]) -> dict[str, Any]:
    full_runs: list[dict[str, Any]] = []
    source_suites: list[dict[str, Any]] = []
    for suite_dir in suite_dirs:
        suite_path = suite_dir / "suite.json"
        if not suite_path.is_file():
            raise FileNotFoundError(f"missing suite.json: {suite_path}")
        suite = _load_json(suite_path)
        source_suites.append(
            {
                "suite_dir": str(suite_dir),
                "suite_json": str(suite_path),
                "summary": suite.get("summary") if isinstance(suite.get("summary"), dict) else {},
            }
        )
        for entry in suite.get("runs") or []:
            if not isinstance(entry, dict):
                continue
            run = _load_full_run(entry, suite_dir)
            run["pilot_source_suite"] = str(suite_dir)
            full_runs.append(run)

    payload = {
        "mode": "openhands-pilot-summary",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "output_dir": str(output_dir),
        "source_suites": source_suites,
        "summary": rebuild_suite_summary(full_runs),
        "agent_usage_totals": _sum_agent_usage(full_runs),
        "runs": [compact_suite_run_entry(run) for run in full_runs],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_json = output_dir / "pilot5-summary.json"
    summary_md = output_dir / "pilot5-summary.md"
    summary_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    summary_md.write_text(_render_markdown(payload), encoding="utf-8")
    return payload


def _load_full_run(entry: dict[str, Any], suite_dir: Path) -> dict[str, Any]:
    task_id = entry.get("task_id")
    run_json = entry.get("run_json")
    run_path = Path(run_json) if isinstance(run_json, str) and run_json else None
    if run_path is None and isinstance(task_id, str) and task_id:
        run_path = suite_dir / task_id / "run.json"
    if run_path is not None and run_path.is_file():
        return _load_json(run_path)
    return _inflate_compact_run(entry)


def _inflate_compact_run(entry: dict[str, Any]) -> dict[str, Any]:
    agent_usage = entry.get("agent_usage") if isinstance(entry.get("agent_usage"), dict) else {}
    return {
        "task_id": entry.get("task_id", ""),
        "status": entry.get("status", "failed"),
        "run_json": entry.get("run_json", ""),
        "agent": {
            "passed": entry.get("status") == "passed",
            "usage": agent_usage,
        },
        "submission": {
            "exists": entry.get("status") != "missing_submission",
            "recovered": entry.get("submission_recovered") is True,
        },
        "evaluation": {
            "result_json": entry.get("result_json", ""),
            "scores": {"final_score": entry.get("final_score", 0.0)},
            "resource_limited": entry.get("resource_limited") is True,
            "log_limit_exceeded": entry.get("log_limit_exceeded") is True,
            "docker_sandbox_error": entry.get("docker_sandbox_error") is True,
            "sandbox_backend": entry.get("sandbox_backend", ""),
        },
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    lines = [
        "# OpenHands Pilot5 Summary",
        "",
        f"- Total: {summary.get('total', 0)}",
        f"- Passed: {summary.get('passed', 0)}",
        f"- Failed: {summary.get('failed', 0)}",
        f"- Agent failures: {summary.get('agent_failures', 0)}",
        f"- Missing submissions: {summary.get('missing_submissions', 0)}",
        f"- Log-limit failures: {summary.get('log_limit_failures', 0)}",
        f"- Docker sandbox failures: {summary.get('docker_sandbox_failures', 0)}",
        f"- Average final score: {summary.get('average_final_score', 0.0)}",
        "",
        "## Source Suites",
        "",
    ]
    for source in payload.get("source_suites") or []:
        if not isinstance(source, dict):
            continue
        source_summary = source.get("summary") if isinstance(source.get("summary"), dict) else {}
        lines.append(
            f"- {source.get('suite_dir', '')}: "
            f"{source_summary.get('total', 0)} tasks, {source_summary.get('passed', 0)} passed"
        )
    lines.extend(["", "## Runs", "", "| Task | Status | Final Score |", "| --- | --- | ---: |"])
    for run in payload.get("runs") or []:
        if not isinstance(run, dict):
            continue
        lines.append(
            f"| {run.get('task_id', '')} | {run.get('status', '')} | {run.get('final_score', 0.0)} |"
        )
    lines.append("")
    return "\n".join(lines)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("suite_dirs", nargs="+", type=Path)
    args = parser.parse_args()
    payload = merge_pilot_suites(
        args.output_dir.resolve(),
        [suite_dir.resolve() for suite_dir in args.suite_dirs],
    )
    summary = payload["summary"]
    print(
        "merged pilot summary: total={total} passed={passed} failed={failed}".format(
            total=summary.get("total", 0),
            passed=summary.get("passed", 0),
            failed=summary.get("failed", 0),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
