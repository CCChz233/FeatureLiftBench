#!/usr/bin/env python3
"""Evaluate oracle submissions for all benchmark tasks."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "harness"))

from featureliftbench.docker_eval import evaluate_submission_docker
from featureliftbench.evaluator import evaluate_submission
from featureliftbench.paths import SUBMISSIONS_DIR, TASKS_DIR


def list_task_dirs(task_ids: list[str] | None = None) -> list[Path]:
    if task_ids:
        return [TASKS_DIR / task_id for task_id in task_ids]
    return sorted(
        path for path in TASKS_DIR.iterdir() if path.is_dir() and (path / "metadata.json").is_file()
    )


def evaluate_oracle(
    task_dir: Path,
    oracle_dir: Path,
    eval_output: Path,
    *,
    use_docker: bool,
) -> dict[str, object]:
    if use_docker:
        return evaluate_submission_docker(task_dir, oracle_dir, eval_output, use_docker=True)
    return evaluate_submission(task_dir, oracle_dir, eval_output)


def verify_oracles(
    task_dirs: list[Path],
    *,
    require_present: bool = True,
    use_docker: bool = False,
) -> list[dict[str, object]]:
    reports: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="flb-oracle-verify-") as tmp:
        output_root = Path(tmp)
        for task_dir in task_dirs:
            task_id = task_dir.name
            oracle_dir = SUBMISSIONS_DIR / task_id / "oracle"
            report: dict[str, object] = {
                "task_id": task_id,
                "oracle_dir": str(oracle_dir),
                "present": oracle_dir.is_dir(),
            }
            if not oracle_dir.is_dir():
                report["status"] = "missing"
                report["passed"] = False
                if require_present:
                    report["error"] = "oracle submission directory not found"
                reports.append(report)
                continue

            eval_output = output_root / task_id
            eval_output.mkdir(parents=True, exist_ok=True)
            try:
                result = evaluate_oracle(
                    task_dir,
                    oracle_dir,
                    eval_output,
                    use_docker=use_docker,
                )
            except Exception as exc:  # noqa: BLE001 - aggregate failures for script output
                report["status"] = "error"
                report["passed"] = False
                report["error"] = str(exc)
                reports.append(report)
                continue

            scores = result.get("scores") or {}
            report["status"] = result.get("status", "unknown")
            report["passed"] = result.get("status") == "passed"
            report["functional_gate"] = scores.get("functional_gate")
            report["final_score"] = scores.get("final_score")
            if not report["passed"]:
                errors = result.get("errors") or []
                report["error"] = "; ".join(str(item) for item in errors) or result.get("reason")
            reports.append(report)
    return reports


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--task-id",
        action="append",
        dest="task_ids",
        help="Limit to specific task_id (repeatable)",
    )
    parser.add_argument("--json", type=Path, help="Write JSON report to this path")
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Do not count missing oracle directories as failures",
    )
    parser.add_argument(
        "--docker",
        action="store_true",
        help="evaluate oracles inside the featureliftbench-eval Docker image",
    )
    args = parser.parse_args()

    task_dirs = list_task_dirs(args.task_ids)
    reports = verify_oracles(
        task_dirs,
        require_present=not args.allow_missing,
        use_docker=args.docker,
    )

    passed = [report for report in reports if report.get("passed")]
    missing = [report for report in reports if report.get("status") == "missing"]
    failed = [
        report
        for report in reports
        if not report.get("passed") and report.get("status") != "missing"
    ]

    for report in reports:
        status = report.get("status", "unknown")
        mark = "PASS" if report.get("passed") else status.upper()
        print(f"[{mark}] {report['task_id']}")
        if report.get("error"):
            print(f"  {report['error']}")

    print()
    print(
        f"Verified {len(reports)} tasks: "
        f"{len(passed)} passed, {len(failed)} failed, {len(missing)} missing."
    )

    payload = {
        "summary": {
            "total": len(reports),
            "passed": len(passed),
            "failed": len(failed),
            "missing": len(missing),
        },
        "reports": reports,
    }
    if args.json:
        args.json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        print(f"Wrote report to {args.json}")

    failures = len(failed)
    if not args.allow_missing:
        failures += len(missing)
    raise SystemExit(failures)


if __name__ == "__main__":
    main()
