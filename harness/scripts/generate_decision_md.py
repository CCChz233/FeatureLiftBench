#!/usr/bin/env python3
"""Generate decision.md from gate_report.json for batch-1 tasks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO / "harness"))

from generate_gate_report import list_batch1_task_ids


def render_decision(task_id: str, gate: dict[str, object]) -> str:
    decision = gate.get("decision", "pending_flash")
    flash_tier = gate.get("flash_tier", "not_run")
    blocking = gate.get("blocking_gates") or []
    metrics = gate.get("metrics") or {}

    b_tier_note = ""
    if flash_tier == "B":
        b_tier_note = (
            "\n\nB-tier exception: Flash passed with near-oracle extraction; "
            "promoted under batch-1 B-tier budget with `large-closure-pass` tag."
        )

    blocking_section = "- none" if not blocking else "\n".join(f"- {g}" for g in blocking)

    return f"""# Review: {task_id}

Decision: {decision}
Flash tier: {flash_tier}
Quality score: pending manual scorecard

## Evidence

- gate report: experiments/batch1/{task_id}/review/gate_report.json
- oracle: experiments/batch1/{task_id}/review/oracle/result.json
- naive: experiments/batch1/{task_id}/review/naive/result.json
- copy_all: experiments/batch1/{task_id}/review/copy_all/result.json
- flash: experiments/batch1/{task_id}/review/flash/run.json

## Metrics

| Baseline | Extraction | Final |
| --- | ---: | ---: |
| oracle | {metrics.get('oracle_extraction')} | {metrics.get('oracle_final')} |
| naive | {metrics.get('naive_extraction')} | — |
| copy_all | {metrics.get('copy_all_extraction')} | — |
| flash | {metrics.get('flash_extraction')} | {metrics.get('flash_final')} |

## Blocking Gates

{blocking_section}
{b_tier_note}

## Required Follow-up

- none
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_ids", nargs="*")
    parser.add_argument("--all-batch1", action="store_true")
    args = parser.parse_args()

    task_ids = list_batch1_task_ids() if (args.all_batch1 or not args.task_ids) else args.task_ids
    for task_id in task_ids:
        gate_path = _REPO / "experiments" / "batch1" / task_id / "review" / "gate_report.json"
        if not gate_path.is_file():
            print(f"SKIP {task_id}: no gate_report.json")
            continue
        gate = json.loads(gate_path.read_text(encoding="utf-8"))
        out = gate_path.parent / "decision.md"
        out.write_text(render_decision(task_id, gate), encoding="utf-8")
        print(f"Wrote {out.relative_to(_REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
