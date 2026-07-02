#!/usr/bin/env python3
"""Summarize suite infrastructure health for full benchmark runs."""

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

INFRA_OK_FAILURE_CLASSES = frozenset({"passed", "model_failed"})


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object: {path}")
    return data


def summarize_suite_infra(suite_dir: Path) -> dict[str, Any]:
    suite_path = suite_dir / "suite.json"
    if not suite_path.is_file():
        raise FileNotFoundError(f"missing suite.json: {suite_path}")

    suite = _load_json(suite_path)
    summary = suite.get("summary") if isinstance(suite.get("summary"), dict) else {}
    runs = suite.get("runs") if isinstance(suite.get("runs"), list) else []
    agent_usage_totals = (
        suite.get("agent_usage_totals")
        if isinstance(suite.get("agent_usage_totals"), dict)
        else {}
    )

    failure_classes = summary.get("failure_classes")
    if not isinstance(failure_classes, dict):
        failure_classes = {}

    infra_failure_classes = {
        key: value
        for key, value in failure_classes.items()
        if key not in INFRA_OK_FAILURE_CLASSES and isinstance(value, int) and value > 0
    }
    infra_clean = not infra_failure_classes

    max_prompt_tokens_per_call = 0
    usage_unverified_runs = 0
    for run in runs:
        if not isinstance(run, dict):
            continue
        task_id = str(run.get("task_id") or "")
        task_dir = suite_dir / task_id
        run_json_path = Path(run.get("run_json") or task_dir / "run.json")
        if not run_json_path.is_file():
            continue
        try:
            detail = _load_json(run_json_path)
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        agent = detail.get("agent") if isinstance(detail.get("agent"), dict) else {}
        usage = agent.get("usage") if isinstance(agent.get("usage"), dict) else {}
        context_audit = usage.get("context_audit") if isinstance(usage.get("context_audit"), dict) else {}
        max_prompt = context_audit.get("max_prompt_tokens_per_call")
        if isinstance(max_prompt, int):
            max_prompt_tokens_per_call = max(max_prompt_tokens_per_call, max_prompt)
        if context_audit.get("usage_unverified") is True:
            usage_unverified_runs += 1

    return {
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "suite_dir": str(suite_dir.resolve()),
        "total": summary.get("total", len(runs)),
        "passed": summary.get("passed", 0),
        "failure_classes": failure_classes,
        "infra_failure_classes": infra_failure_classes,
        "infra_clean": infra_clean,
        "agent_failures": summary.get("agent_failures", 0),
        "docker_sandbox_failures": summary.get("docker_sandbox_failures", 0),
        "log_limit_failures": summary.get("log_limit_failures", 0),
        "usage_unverified_runs": usage_unverified_runs,
        "max_prompt_tokens_per_call": max_prompt_tokens_per_call,
        "agent_usage_totals": agent_usage_totals,
        "task_cooldown_seconds": suite.get("task_cooldown_seconds", 0),
        "eval_backend": suite.get("eval_backend", ""),
        "agent_backend": suite.get("agent_backend", ""),
    }


def _render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Suite Infrastructure Summary",
        "",
        f"- Generated: {summary['generated_at']}",
        f"- Suite: `{summary['suite_dir']}`",
        f"- Infra clean: **{summary['infra_clean']}**",
        f"- Passed: {summary['passed']}/{summary['total']}",
        f"- Usage unverified runs: {summary['usage_unverified_runs']}",
        f"- Max prompt tokens per call: {summary['max_prompt_tokens_per_call']}",
        "",
        "## Failure classes",
        "",
    ]
    failure_classes = summary.get("failure_classes") or {}
    if failure_classes:
        for key in sorted(failure_classes):
            lines.append(f"- {key}: {failure_classes[key]}")
    else:
        lines.append("- (none recorded)")
    lines.extend(
        [
            "",
            "## Infra blockers",
            "",
        ]
    )
    infra_failure_classes = summary.get("infra_failure_classes") or {}
    if infra_failure_classes:
        for key in sorted(infra_failure_classes):
            lines.append(f"- {key}: {infra_failure_classes[key]}")
    else:
        lines.append("- none")
    usage_totals = summary.get("agent_usage_totals") or {}
    if usage_totals:
        lines.extend(
            [
                "",
                "## Agent usage totals",
                "",
                f"- total_tokens: {usage_totals.get('total_tokens', 0)}",
                f"- api_calls: {usage_totals.get('api_calls', 0)}",
                f"- prompt_tokens: {usage_totals.get('prompt_tokens', 0)}",
                f"- completion_tokens: {usage_totals.get('completion_tokens', 0)}",
            ]
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("suite_dir", type=Path, help="Directory containing suite.json")
    parser.add_argument(
        "--output-prefix",
        type=Path,
        default=None,
        help="Output prefix without suffix (default: <suite_dir>/infra-summary)",
    )
    args = parser.parse_args()

    suite_dir = args.suite_dir.resolve()
    summary = summarize_suite_infra(suite_dir)
    prefix = args.output_prefix or (suite_dir / "infra-summary")
    prefix.parent.mkdir(parents=True, exist_ok=True)

    json_path = prefix.with_suffix(".json")
    md_path = prefix.with_suffix(".md")
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_render_markdown(summary), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(f"infra_clean={summary['infra_clean']}")
    return 0 if summary["infra_clean"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
