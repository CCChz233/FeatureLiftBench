#!/usr/bin/env python3
"""Audit allowed_dependencies vs requirements.lock across benchmark tasks."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "harness"))

from featureliftbench.dependency_audit import audit_task_root  # noqa: E402
from featureliftbench.paths import TASKS_DIR  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=TASKS_DIR,
        help="Task dataset root (default: benchmark/tasks)",
    )
    parser.add_argument(
        "--skip-wheels",
        action="store_true",
        help="do not require vendor wheels for locked dependencies",
    )
    parser.add_argument(
        "--skip-oracle",
        action="store_true",
        help="do not compare oracle_manifest runtime_dependencies",
    )
    parser.add_argument("--json", type=Path, help="write machine-readable report")
    args = parser.parse_args()

    audits = audit_task_root(
        args.root.resolve(),
        check_wheels=not args.skip_wheels,
        check_oracle_manifest=not args.skip_oracle,
    )
    failing = [audit for audit in audits if not audit.ok]

    for audit in failing:
        for issue in audit.issues:
            print(f"[{issue.kind}] {audit.task_id}: {issue.message}")

    counts = Counter(issue.kind for audit in failing for issue in audit.issues)
    print()
    print(
        f"Audited {len(audits)} tasks: {len(audits) - len(failing)} ok, "
        f"{len(failing)} with issues."
    )
    if counts:
        print("Issue kinds:", dict(counts))

    if args.json:
        payload = {
            "root": str(args.root.resolve()),
            "summary": {
                "total": len(audits),
                "ok": len(audits) - len(failing),
                "failed": len(failing),
                "issue_kinds": dict(counts),
            },
            "tasks": [
                {
                    "task_id": audit.task_id,
                    "allowed": audit.allowed,
                    "locked": audit.locked,
                    "issues": [
                        {"kind": issue.kind, "message": issue.message}
                        for issue in audit.issues
                    ],
                }
                for audit in audits
            ],
        }
        args.json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Wrote {args.json}")

    return 1 if failing else 0


if __name__ == "__main__":
    raise SystemExit(main())
