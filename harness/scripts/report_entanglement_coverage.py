#!/usr/bin/env python3
"""Report task counts and optional suite pass rates by entanglement.primary."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "harness"))

from featureliftbench.metadata import ENTANGLEMENT_PRIMARY_TYPES
from featureliftbench.paths import TASKS_DIR


def load_suite_results(suite_dir: Path) -> dict[str, bool]:
    suite_path = suite_dir / "suite.json"
    if not suite_path.is_file():
        return {}
    suite = json.loads(suite_path.read_text(encoding="utf-8"))
    return {
        run["task_id"]: run.get("status") == "passed"
        for run in suite.get("runs", [])
        if isinstance(run, dict) and isinstance(run.get("task_id"), str)
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--suite-dir",
        type=Path,
        help="Optional run-agent output directory with suite.json",
    )
    args = parser.parse_args()
    results = load_suite_results(args.suite_dir.resolve()) if args.suite_dir else {}

    stats: dict[str, dict[str, int]] = {
        primary: {"total": 0, "passed": 0} for primary in ENTANGLEMENT_PRIMARY_TYPES
    }
    missing_primary: list[str] = []

    for task_dir in sorted(TASKS_DIR.iterdir()):
        meta_path = task_dir / "metadata.json"
        if not meta_path.is_file():
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        task_id = meta.get("task_id", task_dir.name)
        ent = meta.get("entanglement", {})
        primary = ent.get("primary") if isinstance(ent, dict) else None
        if not isinstance(primary, str) or not primary:
            missing_primary.append(task_id)
            continue
        stats.setdefault(primary, {"total": 0, "passed": 0})
        stats[primary]["total"] += 1
        if results.get(task_id):
            stats[primary]["passed"] += 1

    print(f"{'primary':<40} {'tasks':>5} {'pass':>5} {'rate':>7}")
    for primary in ENTANGLEMENT_PRIMARY_TYPES:
        row = stats.get(primary, {"total": 0, "passed": 0})
        rate = (
            f"{100 * row['passed'] / row['total']:.0f}%"
            if row["total"] and results
            else ("—" if row["total"] else "—")
        )
        pass_col = str(row["passed"]) if results else "—"
        print(f"{primary:<40} {row['total']:>5} {pass_col:>5} {rate:>7}")

    if missing_primary:
        print(f"\nTasks missing entanglement.primary: {', '.join(missing_primary)}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
