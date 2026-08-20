#!/usr/bin/env python3
"""Compare Core-12 screening suites: Pass, tokens, steps, and B process metrics."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "harness"))

from featureliftbench.suite_utils import effective_agent_usage_for_run
from featureliftbench.suite_utils import functional_gate_value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare Core-12 condenser / pre-submit audit suites"
    )
    parser.add_argument(
        "suite_dirs",
        nargs="+",
        type=Path,
        help="One or more suite output directories containing suite.json",
    )
    args = parser.parse_args()
    rows = [summarize_suite(path) for path in args.suite_dirs]
    print(json.dumps({"suites": rows}, indent=2, sort_keys=True))
    _print_table(rows)
    return 0


def summarize_suite(suite_dir: Path) -> dict[str, Any]:
    suite_path = suite_dir / "suite.json"
    payload = json.loads(suite_path.read_text(encoding="utf-8"))
    runs = payload.get("runs") if isinstance(payload.get("runs"), list) else []
    passed = 0
    prompt_tokens = 0
    completion_tokens = 0
    steps = 0
    audit_executed = 0
    gap_found = 0
    continued = 0
    for run in runs:
        if not isinstance(run, dict):
            continue
        if functional_gate_value(run) == 1.0:
            passed += 1
        usage = effective_agent_usage_for_run(run)
        prompt_tokens += int(usage.get("prompt_tokens") or 0)
        completion_tokens += int(usage.get("completion_tokens") or 0)
        steps += int(usage.get("assistant_steps") or 0)
        audit = _load_pre_submit_audit(suite_dir, run)
        if audit.get("audit_executed") is True:
            audit_executed += 1
        if audit.get("explicit_gap_found") is True:
            gap_found += 1
        if audit.get("continued_after_gap") is True:
            continued += 1
    total = len(runs)
    return {
        "suite_dir": str(suite_dir),
        "n": total,
        "functional_passed": passed,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "assistant_steps": steps,
        "audit_executed": audit_executed,
        "explicit_gap_found": gap_found,
        "continued_after_gap": continued,
    }


def _load_pre_submit_audit(suite_dir: Path, run: dict[str, Any]) -> dict[str, Any]:
    task_id = str(run.get("task_id") or "")
    candidates = [
        suite_dir / task_id / "agent" / "pre_submit_audit.json",
        Path(str(run.get("run_json") or "")).parent / "agent" / "pre_submit_audit.json",
    ]
    for path in candidates:
        if path.is_file():
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return {}
            return payload if isinstance(payload, dict) else {}
    return {}


def _print_table(rows: list[dict[str, Any]]) -> None:
    print()
    print(
        f"{'suite':<48} {'pass':>5} {'tokens':>12} {'steps':>8} "
        f"{'audit':>6} {'gaps':>5} {'cont':>5}"
    )
    for row in rows:
        name = Path(row["suite_dir"]).name[:48]
        print(
            f"{name:<48} {row['functional_passed']:>2}/{row['n']:<2} "
            f"{row['total_tokens']:>12} {row['assistant_steps']:>8} "
            f"{row['audit_executed']:>6} {row['explicit_gap_found']:>5} "
            f"{row['continued_after_gap']:>5}"
        )


if __name__ == "__main__":
    raise SystemExit(main())
