#!/usr/bin/env python3
"""Update design note Status from batch-1 gate_report.json."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO / "harness" / "scripts") not in sys.path:
    sys.path.insert(0, str(_REPO / "harness" / "scripts"))

from generate_gate_report import list_batch1_task_ids

STATUS_RE = re.compile(r"^Status:.*$", re.MULTILINE)


def status_line(decision: str, flash_tier: str) -> str:
    if decision != "promote":
        return f"Status: gate review ({decision}, flash {flash_tier})"
    if flash_tier == "A":
        return "Status: agent-calibrated"
    if flash_tier == "B":
        return "Status: agent-calibrated (B-tier exception promote)"
    return f"Status: agent-calibrated (flash {flash_tier})"


def main() -> int:
    for task_id in list_batch1_task_ids():
        gate_path = _REPO / "experiments" / "batch1" / task_id / "review" / "gate_report.json"
        design_path = _REPO / "docs" / "task_designs" / f"{task_id}.md"
        if not gate_path.is_file() or not design_path.is_file():
            continue
        gate = json.loads(gate_path.read_text(encoding="utf-8"))
        new_status = status_line(str(gate.get("decision", "")), str(gate.get("flash_tier", "not_run")))
        text = design_path.read_text(encoding="utf-8")
        if STATUS_RE.search(text):
            text = STATUS_RE.sub(new_status, text, count=1)
        else:
            text = text.replace(f"# Task Design: `{task_id}`\n", f"# Task Design: `{task_id}`\n\n{new_status}\n", 1)
        design_path.write_text(text, encoding="utf-8")
        print(f"Updated {design_path.name}: {new_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
