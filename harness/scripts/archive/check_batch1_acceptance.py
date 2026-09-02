#!/usr/bin/env python3
"""Check batch-1 quality acceptance evidence completeness."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO / "harness"))

from generate_gate_report import list_batch1_task_ids

REQUIRED_FILES = (
    "validate-task.log",
    "audit-output-imports.log",
    "module-probes.log",
    "oracle/result.json",
    "naive/result.json",
    "copy_all/result.json",
    "gate_report.json",
    "decision.md",
    "flash/run.json",
)


def check_task(task_id: str) -> dict[str, object]:
    review = _REPO / "experiments" / "batch1" / task_id / "review"
    missing = [name for name in REQUIRED_FILES if not (review / name).is_file()]
    gate: dict[str, object] = {}
    if (review / "gate_report.json").is_file():
        gate = json.loads((review / "gate_report.json").read_text(encoding="utf-8"))
    return {
        "task_id": task_id,
        "missing": missing,
        "decision": gate.get("decision"),
        "flash_tier": gate.get("flash_tier"),
        "blocking_gates": gate.get("blocking_gates", []),
        "complete": not missing and gate.get("decision") == "promote" and not gate.get("blocking_gates"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    reports = [check_task(tid) for tid in list_batch1_task_ids()]
    complete = sum(1 for r in reports if r["complete"])
    missing_gate = sum(1 for r in reports if "gate_report.json" in r["missing"])
    missing_flash = sum(1 for r in reports if "flash/run.json" in r["missing"])
    missing_decision = sum(1 for r in reports if "decision.md" in r["missing"])
    not_promote = [r for r in reports if r.get("decision") != "promote"]

    summary = {
        "batch1_tasks": len(reports),
        "fully_accepted": complete,
        "missing_gate_report": missing_gate,
        "missing_decision_md": missing_decision,
        "missing_flash_run": missing_flash,
        "not_promote_decision": len(not_promote),
        "tasks": reports,
    }

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"batch-1 tasks: {len(reports)}")
        print(f"fully accepted: {complete}/{len(reports)}")
        print(f"missing gate_report: {missing_gate}")
        print(f"missing decision.md: {missing_decision}")
        print(f"missing flash/run.json: {missing_flash}")
        print(f"decision != promote: {len(not_promote)}")
        if not_promote:
            for r in not_promote[:15]:
                print(
                    f"  {r['task_id']}: decision={r.get('decision')} "
                    f"flash={r.get('flash_tier')} blocking={r.get('blocking_gates')}"
                )

    return 0 if complete == len(reports) else 1


if __name__ == "__main__":
    raise SystemExit(main())
