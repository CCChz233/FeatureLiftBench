#!/usr/bin/env python3
"""Import existing mini-swe-agent Flash runs into batch-1 review packets."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO / "harness" / "scripts") not in sys.path:
    sys.path.insert(0, str(_REPO / "harness" / "scripts"))

from generate_gate_report import list_batch1_task_ids, generate_gate_report


def import_flash(task_id: str) -> bool:
    candidates = [
        _REPO / "experiments" / "mini-swe-agent" / f"{task_id}-flash-001" / "run.json",
        _REPO / "experiments" / "mini-swe-agent" / f"{task_id}-flash-001" / "result.json",
        _REPO / "experiments" / "batch1" / task_id / "review" / "flash" / "result.json",
    ]
    src = next((p for p in candidates if p.is_file()), None)
    if src is None:
        return False
    dest_dir = _REPO / "experiments" / "batch1" / task_id / "review" / "flash"
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest_dir / "run.json")
    report = generate_gate_report(task_id)
    out = _REPO / "experiments" / "batch1" / task_id / "review" / "gate_report.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{task_id}: imported flash tier={report['flash_tier']} decision={report['decision']}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_ids", nargs="*")
    parser.add_argument("--all-batch1", action="store_true")
    args = parser.parse_args()
    task_ids = list_batch1_task_ids() if (args.all_batch1 or not args.task_ids) else args.task_ids
    imported = sum(1 for tid in task_ids if import_flash(tid))
    print(f"Imported {imported}/{len(task_ids)} flash runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
