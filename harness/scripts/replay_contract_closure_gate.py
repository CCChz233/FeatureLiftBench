#!/usr/bin/env python3
"""Replay structure-only Contract Closure Gate checks on archived submissions."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "harness"))

from featureliftbench.contract_closure_gate import check_workspace  # noqa: E402
from featureliftbench.contract_closure_gate import (  # noqa: E402
    install_contract_closure_workspace,
)
from featureliftbench.contract_closure_gate.common import (  # noqa: E402
    CHECKER_VERSION,
)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _find_task(task_id: str, task_roots: list[Path]) -> Path | None:
    for root in task_roots:
        candidate = root / task_id
        if (candidate / "metadata.json").is_file():
            return candidate
    return None


def _old_environment_only(report: dict[str, Any]) -> bool:
    failures = [
        item
        for item in report.get("checks") or []
        if isinstance(item, dict)
        and item.get("status") == "fail"
        and item.get("severity") == "hard"
    ]
    return bool(report.get("repair_needed") and failures) and all(
        "dependency import failed:" in str(item.get("message") or "")
        for item in failures
    )


def _formal_gate(task_run_dir: Path) -> float | None:
    result_path = task_run_dir / "eval" / "result.json"
    if not result_path.is_file():
        return None
    scores = _load_json(result_path).get("scores")
    value = scores.get("functional_gate") if isinstance(scores, dict) else None
    return float(value) if isinstance(value, (int, float)) else None


def _archived_repair_usage(task_run_dir: Path) -> dict[str, float]:
    run_path = task_run_dir / "run.json"
    if not run_path.is_file():
        return {}
    run = _load_json(run_path)
    closure = run.get("contract_closure")
    totals = closure.get("usage_totals") if isinstance(closure, dict) else None
    phases = totals.get("phases") if isinstance(totals, dict) else None
    if not isinstance(phases, list):
        return {}
    repair = next(
        (
            phase
            for phase in phases
            if isinstance(phase, dict) and phase.get("phase") == "repair"
        ),
        None,
    )
    if not isinstance(repair, dict):
        return {}
    return {
        key: float(repair[key])
        for key in ("total_tokens", "duration_seconds", "api_calls", "assistant_steps")
        if isinstance(repair.get(key), (int, float))
    }


def _replay_one(
    suite_dir: Path,
    task_id: str,
    task_roots: list[Path],
) -> dict[str, Any]:
    task_run_dir = suite_dir / task_id
    submission = task_run_dir / "submission"
    task_dir = _find_task(task_id, task_roots)
    old_initial_path = task_run_dir / "contract_closure_initial.json"
    old_initial = _load_json(old_initial_path) if old_initial_path.is_file() else {}
    row: dict[str, Any] = {
        "task_id": task_id,
        "formal_functional_gate": _formal_gate(task_run_dir),
        "old_initial_repair_needed": old_initial.get("repair_needed"),
        "old_initial_environment_only": _old_environment_only(old_initial),
        "archived_repair_usage": _archived_repair_usage(task_run_dir),
    }
    if task_dir is None:
        return {**row, "replay_error": "task metadata not found"}
    if not submission.is_dir():
        return {**row, "replay_error": "submission directory not found"}

    metadata = _load_json(task_dir / "metadata.json")
    with tempfile.TemporaryDirectory(prefix=f"flb-closure-replay-{task_id[:24]}-") as tmp:
        workspace = Path(tmp)
        install_contract_closure_workspace(workspace, metadata=metadata, lite=True)
        shutil.copytree(submission, workspace / "submission", dirs_exist_ok=True)
        try:
            replay = check_workspace(workspace, check_mode="structure")
        except Exception as exc:  # noqa: BLE001 - preserve the whole replay audit
            return {**row, "replay_error": f"{type(exc).__name__}: {exc}"}

    return {
        **row,
        "replay_hard_gate_ok": replay.get("hard_gate_ok"),
        "replay_repair_needed": replay.get("repair_needed"),
        "replay_hard_failure_count": replay.get("hard_failure_count"),
        "replay_unknown_count": replay.get("unknown_count"),
        "replay_checker_environment_unknown_count": replay.get(
            "checker_environment_unknown_count", 0
        ),
        "replay_failed_checks": [
            {
                key: item.get(key)
                for key in ("id", "category", "status", "severity", "message")
            }
            for item in replay.get("checks") or []
            if isinstance(item, dict) and item.get("status") == "fail"
        ],
    }


def replay_suite(
    suite_dir: Path,
    *,
    task_roots: list[Path],
    workers: int,
) -> dict[str, Any]:
    suite = _load_json(suite_dir / "suite.json")
    task_ids = [
        str(run.get("task_id"))
        for run in suite.get("runs") or []
        if isinstance(run, dict) and run.get("task_id")
    ]
    rows: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        futures = {
            executor.submit(_replay_one, suite_dir, task_id, task_roots): task_id
            for task_id in task_ids
        }
        for future in as_completed(futures):
            rows.append(future.result())
    rows.sort(key=lambda row: str(row.get("task_id") or ""))

    replayed = [row for row in rows if not row.get("replay_error")]
    formal_failures = [row for row in replayed if row.get("formal_functional_gate") == 0.0]
    hard_open = [row for row in replayed if row.get("replay_hard_gate_ok") is False]
    hard_open_formal_failures = [
        row for row in hard_open if row.get("formal_functional_gate") == 0.0
    ]
    summary = {
        "assigned": len(task_ids),
        "replayed": len(replayed),
        "replay_errors": len(rows) - len(replayed),
        "archived_initial_repair_requested": sum(
            row.get("old_initial_repair_needed") is True for row in rows
        ),
        "projected_initial_repairs_avoided_environment_only": sum(
            row.get("old_initial_environment_only") is True for row in rows
        ),
        "projected_repair_tokens_avoided_environment_only": int(
            sum(
                (row.get("archived_repair_usage") or {}).get("total_tokens", 0)
                for row in rows
                if row.get("old_initial_environment_only") is True
            )
        ),
        "projected_repair_duration_seconds_avoided_environment_only": round(
            sum(
                (row.get("archived_repair_usage") or {}).get("duration_seconds", 0)
                for row in rows
                if row.get("old_initial_environment_only") is True
            ),
            3,
        ),
        "replayed_final_hard_open": len(hard_open),
        "replayed_final_repair_requested": sum(
            row.get("replay_repair_needed") is True for row in replayed
        ),
        "replayed_final_with_checker_environment_unknown": sum(
            int(row.get("replay_checker_environment_unknown_count") or 0) > 0
            for row in replayed
        ),
        "formal_failures_with_result": len(formal_failures),
        "hard_open_formal_failures": len(hard_open_formal_failures),
        "hard_open_precision_for_formal_failure": (
            round(len(hard_open_formal_failures) / len(hard_open), 6)
            if hard_open
            else None
        ),
    }
    return {
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "checker_version": CHECKER_VERSION,
        "suite_dir": str(suite_dir),
        "submission_snapshot": "archived post-repair final submission",
        "task_roots": [str(path) for path in task_roots],
        "summary": summary,
        "runs": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("suite_dir", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument(
        "--task-root",
        action="append",
        type=Path,
        dest="task_roots",
        help="Task root; may be repeated (defaults to Python-200 roots)",
    )
    args = parser.parse_args()
    suite_dir = args.suite_dir.resolve()
    task_roots = args.task_roots or [
        _REPO_ROOT / "benchmark" / "tasks",
        _REPO_ROOT / "benchmark" / "external50",
    ]
    payload = replay_suite(
        suite_dir,
        task_roots=[path.resolve() for path in task_roots],
        workers=args.workers,
    )
    output = args.output or suite_dir / f"contract-closure-replay-{CHECKER_VERSION}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(f"Wrote {output}")
    return 0 if payload["summary"]["replay_errors"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
