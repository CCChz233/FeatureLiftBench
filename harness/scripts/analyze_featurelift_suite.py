#!/usr/bin/env python3
"""Analyze a featurelift-agent suite run with context/tool audit fields."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC
from datetime import datetime
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


def _task_row(suite_dir: Path, run: dict[str, Any]) -> dict[str, Any]:
    task_id = str(run.get("task_id") or "")
    task_dir = suite_dir / task_id
    run_json_path = Path(run.get("run_json") or task_dir / "run.json")
    detail = _load_json(run_json_path) if run_json_path.is_file() else {}
    agent = detail.get("agent") if isinstance(detail.get("agent"), dict) else {}
    usage = agent.get("usage") if isinstance(agent.get("usage"), dict) else {}
    evaluation = detail.get("evaluation") if isinstance(detail.get("evaluation"), dict) else {}
    scores = evaluation.get("scores") if isinstance(evaluation.get("scores"), dict) else {}
    context_audit = usage.get("context_audit") if isinstance(usage.get("context_audit"), dict) else {}
    tool_summary = usage.get("tool_summary") if isinstance(usage.get("tool_summary"), dict) else {}

    return {
        "task_id": task_id,
        "status": evaluation.get("status") or run.get("status"),
        "final_score": scores.get("final_score", run.get("final_score")),
        "functional_gate": scores.get("functional_gate"),
        "agent_backend": detail.get("agent_backend"),
        "eval_backend": detail.get("eval_backend"),
        "exit_status": usage.get("exit_status"),
        "api_calls": usage.get("api_calls"),
        "total_tokens": usage.get("total_tokens"),
        "context_violation": context_audit.get("context_violation"),
        "usage_unverified": context_audit.get("usage_unverified"),
        "max_prompt_tokens_per_call": context_audit.get("max_prompt_tokens_per_call"),
        "public_tests_status": tool_summary.get("public_tests_status"),
        "final_check_status": tool_summary.get("final_check_status"),
        "run_json": str(run_json_path),
        "usage_json": str(task_dir / "agent" / "usage.json"),
    }


def _render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# FeatureLiftAgent Suite Analysis",
        "",
        f"- Generated: {summary['generated_at']}",
        f"- Suite: `{summary['suite_dir']}`",
        f"- Passed: {summary['passed']}/{summary['total']}",
        f"- Average final score: {summary['average_final_score']}",
        f"- Context violation runs: {summary['context_violation_runs']}",
        f"- Usage unverified runs: {summary['usage_unverified_runs']}",
        "",
        "## Tasks",
        "",
        "| task_id | status | final_score | exit_status | public_tests | final_check | api_calls | max_prompt | context_violation |",
        "| --- | --- | ---: | --- | --- | --- | ---: | ---: | --- |",
    ]
    for row in summary["tasks"]:
        lines.append(
            "| {task_id} | {status} | {final_score} | {exit_status} | {public_tests_status} | "
            "{final_check_status} | {api_calls} | {max_prompt_tokens_per_call} | {context_violation} |".format(
                **row
            )
        )
    lines.append("")
    return "\n".join(lines)


def analyze_featurelift_suite(suite_dir: Path) -> dict[str, Any]:
    suite_path = suite_dir / "suite.json"
    if not suite_path.is_file():
        raise FileNotFoundError(f"missing suite.json: {suite_path}")
    suite = _load_json(suite_path)
    summary = suite.get("summary") if isinstance(suite.get("summary"), dict) else {}
    runs = suite.get("runs") if isinstance(suite.get("runs"), list) else []
    tasks = [_task_row(suite_dir, run) for run in runs if isinstance(run, dict)]

    context_violation_runs = sum(1 for row in tasks if row.get("context_violation") is True)
    usage_unverified_runs = sum(1 for row in tasks if row.get("usage_unverified") is True)

    return {
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "suite_dir": str(suite_dir.resolve()),
        "passed": summary.get("passed", 0),
        "total": summary.get("total", len(tasks)),
        "average_final_score": summary.get("average_final_score", 0.0),
        "context_violation_runs": context_violation_runs,
        "usage_unverified_runs": usage_unverified_runs,
        "tasks": tasks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("suite_dir", type=Path, help="Directory containing suite.json")
    parser.add_argument(
        "--output-prefix",
        type=Path,
        default=None,
        help="Output prefix without suffix (default: <suite_dir>/featurelift-analysis)",
    )
    args = parser.parse_args()

    suite_dir = args.suite_dir.resolve()
    summary = analyze_featurelift_suite(suite_dir)
    prefix = args.output_prefix or (suite_dir / "featurelift-analysis")
    prefix.parent.mkdir(parents=True, exist_ok=True)

    json_path = prefix.with_suffix(".json")
    md_path = prefix.with_suffix(".md")
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_render_markdown(summary), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
