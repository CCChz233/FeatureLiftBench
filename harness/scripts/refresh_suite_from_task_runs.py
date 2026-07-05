#!/usr/bin/env python3
"""Refresh a run-agent suite.json from per-task run.json files."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "harness"))

from featureliftbench.suite_utils import compact_suite_run_entry
from featureliftbench.suite_utils import rebuild_suite_summary

_USAGE_SUM_FIELDS = (
    "assistant_steps",
    "total_messages",
    "api_calls",
    "prompt_tokens",
    "completion_tokens",
    "total_tokens",
    "trace_tokens",
    "billed_tokens",
)


def refresh_suite(suite_dir: Path) -> dict[str, Any]:
    suite_path = suite_dir / "suite.json"
    if not suite_path.is_file():
        raise SystemExit(f"missing suite.json: {suite_path}")

    suite = json.loads(suite_path.read_text(encoding="utf-8"))
    task_ids = [
        run.get("task_id")
        for run in suite.get("runs", [])
        if isinstance(run, dict) and isinstance(run.get("task_id"), str)
    ]

    refreshed: list[dict[str, Any]] = []
    for task_id in task_ids:
        run_path = suite_dir / task_id / "run.json"
        if not run_path.is_file():
            continue
        run = json.loads(run_path.read_text(encoding="utf-8"))
        if isinstance(run, dict):
            refreshed.append(run)

    suite["runs"] = [compact_suite_run_entry(run) for run in refreshed]
    suite["summary"] = rebuild_suite_summary(refreshed)
    suite["agent_usage_totals"] = _sum_agent_usage(refreshed)
    suite_path.write_text(json.dumps(suite, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return suite


def _sum_agent_usage(runs: list[dict[str, Any]]) -> dict[str, Any]:
    totals = {field: 0 for field in _USAGE_SUM_FIELDS}
    available = 0
    missing = 0
    for run in runs:
        agent = run.get("agent") if isinstance(run.get("agent"), dict) else {}
        usage = agent.get("usage") if isinstance(agent.get("usage"), dict) else {}
        if usage.get("available") is True:
            available += 1
        else:
            missing += 1
        for field in _USAGE_SUM_FIELDS:
            value = usage.get(field)
            if isinstance(value, (int, float)):
                totals[field] += value
    return {
        "available_runs": available,
        "missing_runs": missing,
        **totals,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("suite_dir", type=Path)
    args = parser.parse_args()
    suite = refresh_suite(args.suite_dir.resolve())
    summary = suite.get("summary", {})
    print(
        f"refreshed {args.suite_dir}: "
        f"passed={summary.get('passed')} failed={summary.get('failed')} total={summary.get('total')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
