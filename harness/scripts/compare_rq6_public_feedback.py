#!/usr/bin/env python3
"""Compare same-day RQ6 Main vs Public-feedback on Flash-12.

Primary metric is evaluator functional_gate. Also report public/hidden stage
flips. Not a Python-200 main-table result.
"""

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

DEFAULT_SLICE = (
    _REPO_ROOT / "harness/config/experiments/rq6_public_feedback_flash12_v1.json"
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _run_map(suite_dir: Path) -> dict[str, dict[str, Any]]:
    suite = _load_json(suite_dir / "suite.json")
    runs: dict[str, dict[str, Any]] = {}
    for run in suite.get("runs") or []:
        if not isinstance(run, dict):
            continue
        task_id = run.get("task_id")
        if isinstance(task_id, str) and task_id:
            runs[task_id] = run
    return runs


def _eval_result(suite_dir: Path, task_id: str) -> dict[str, Any]:
    path = suite_dir / task_id / "eval" / "result.json"
    if not path.is_file():
        return {
            "available": False,
            "build_pass": None,
            "public_pass": None,
            "hidden_pass": None,
            "functional_gate": None,
        }
    result = _load_json(path)
    public = result.get("public_tests") if isinstance(result.get("public_tests"), dict) else {}
    hidden = result.get("hidden_tests") if isinstance(result.get("hidden_tests"), dict) else {}
    gate = (result.get("scores") or {}).get("functional_gate")
    return {
        "available": True,
        "build_pass": result.get("build_pass"),
        "public_pass": public.get("passed"),
        "hidden_pass": hidden.get("passed"),
        "functional_gate": gate,
    }


def _mounted(suite_dir: Path, task_id: str) -> bool | None:
    run_path = suite_dir / task_id / "run.json"
    if not run_path.is_file():
        return None
    payload = _load_json(run_path)
    workspace = payload.get("workspace") if isinstance(payload.get("workspace"), dict) else {}
    value = workspace.get("public_tests_mounted")
    return value if isinstance(value, bool) else None


def _bool01(value: Any) -> int | None:
    if value is True or value == 1 or value == 1.0:
        return 1
    if value is False or value == 0 or value == 0.0:
        return 0
    return None


def _flip(before: int | None, after: int | None) -> str:
    if before is None or after is None:
        return "unknown"
    if before == 0 and after == 1:
        return "0_to_1"
    if before == 1 and after == 0:
        return "1_to_0"
    if before == after:
        return "unchanged"
    return f"{before}_to_{after}"


def summarize_pair(main_dir: Path, public_dir: Path, slice_path: Path) -> dict[str, Any]:
    slice_payload = _load_json(slice_path)
    cohorts = slice_payload.get("cohorts") or {}
    public_cohort = set(cohorts.get("public_failure") or [])
    hidden_cohort = set(cohorts.get("hidden_failure") or [])
    main_runs = _run_map(main_dir)
    public_runs = _run_map(public_dir)
    task_ids = sorted(set(main_runs) | set(public_runs))

    rows: list[dict[str, Any]] = []
    flips = {
        "public_0_to_1_hidden_still_0": [],
        "hidden_0_to_1": [],
        "functional_0_to_1": [],
        "functional_1_to_0": [],
        "neither_stage_moved": [],
    }
    integrity = {
        "main_not_mounted": 0,
        "public_feedback_mounted": 0,
        "task_set_match": set(main_runs) == set(public_runs),
    }

    for task_id in task_ids:
        main_eval = _eval_result(main_dir, task_id)
        public_eval = _eval_result(public_dir, task_id)
        main_mount = _mounted(main_dir, task_id)
        public_mount = _mounted(public_dir, task_id)
        if main_mount is False:
            integrity["main_not_mounted"] += 1
        if public_mount is True:
            integrity["public_feedback_mounted"] += 1
        main_gate = _bool01(
            main_eval["functional_gate"]
            if main_eval["available"]
            else functional_gate_value(main_runs.get(task_id) or {})
        )
        public_gate = _bool01(
            public_eval["functional_gate"]
            if public_eval["available"]
            else functional_gate_value(public_runs.get(task_id) or {})
        )
        main_public = _bool01(main_eval["public_pass"])
        public_public = _bool01(public_eval["public_pass"])
        main_hidden = _bool01(main_eval["hidden_pass"])
        public_hidden = _bool01(public_eval["hidden_pass"])
        public_flip = _flip(main_public, public_public)
        hidden_flip = _flip(main_hidden, public_hidden)
        gate_flip = _flip(main_gate, public_gate)
        cohort = (
            "public_failure"
            if task_id in public_cohort
            else "hidden_failure"
            if task_id in hidden_cohort
            else "unlisted"
        )
        if public_flip == "0_to_1" and public_hidden == 0:
            flips["public_0_to_1_hidden_still_0"].append(task_id)
        if hidden_flip == "0_to_1":
            flips["hidden_0_to_1"].append(task_id)
        if gate_flip == "0_to_1":
            flips["functional_0_to_1"].append(task_id)
        if gate_flip == "1_to_0":
            flips["functional_1_to_0"].append(task_id)
        if public_flip == "unchanged" and hidden_flip == "unchanged":
            flips["neither_stage_moved"].append(task_id)
        main_usage = effective_agent_usage_for_run(main_runs.get(task_id) or {})
        public_usage = effective_agent_usage_for_run(public_runs.get(task_id) or {})
        rows.append(
            {
                "task_id": task_id,
                "cohort": cohort,
                "main_functional_gate": main_gate,
                "public_feedback_functional_gate": public_gate,
                "main_public": main_public,
                "public_feedback_public": public_public,
                "main_hidden": main_hidden,
                "public_feedback_hidden": public_hidden,
                "public_flip": public_flip,
                "hidden_flip": hidden_flip,
                "functional_flip": gate_flip,
                "main_public_tests_mounted": main_mount,
                "public_feedback_public_tests_mounted": public_mount,
                "main_prompt_tokens": int(main_usage.get("prompt_tokens") or 0),
                "public_feedback_prompt_tokens": int(
                    public_usage.get("prompt_tokens") or 0
                ),
            }
        )

    main_pass = sum(row["main_functional_gate"] == 1 for row in rows)
    public_pass = sum(row["public_feedback_functional_gate"] == 1 for row in rows)
    n = len(rows)
    return {
        "schema_version": "featureliftbench.rq6_public_feedback_pair.v1",
        "main_dir": str(main_dir),
        "public_feedback_dir": str(public_dir),
        "slice": str(slice_path),
        "n": n,
        "functional_passed": {
            "main": main_pass,
            "public_feedback": public_pass,
            "delta": public_pass - main_pass,
        },
        "integrity": integrity,
        "flips": flips,
        "tasks": rows,
        "caveat": (
            "RQ6 explains Main's information boundary. These n=12 numbers do "
            "not go in the Python-200 main table."
        ),
    }


def _print_table(payload: dict[str, Any]) -> None:
    print(
        f"RQ6 Flash-12  functional_gate  "
        f"Main {payload['functional_passed']['main']}/{payload['n']}  "
        f"Public-feedback {payload['functional_passed']['public_feedback']}/{payload['n']}  "
        f"delta {payload['functional_passed']['delta']:+d}"
    )
    print(
        "public 0→1, hidden still 0:",
        ", ".join(payload["flips"]["public_0_to_1_hidden_still_0"]) or "(none)",
    )
    print(
        "hidden 0→1:",
        ", ".join(payload["flips"]["hidden_0_to_1"]) or "(none)",
    )
    print(
        "neither stage moved:",
        ", ".join(payload["flips"]["neither_stage_moved"]) or "(none)",
    )
    print(
        f"{'task':<48} {'cohort':<16} {'gate':<8} {'public':<8} {'hidden':<8}"
    )
    for row in payload["tasks"]:
        print(
            f"{row['task_id']:<48} {row['cohort']:<16} "
            f"{row['main_functional_gate']}→{row['public_feedback_functional_gate']:<5} "
            f"{row['main_public']}→{row['public_feedback_public']:<5} "
            f"{row['main_hidden']}→{row['public_feedback_hidden']}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("main_dir", type=Path)
    parser.add_argument("public_feedback_dir", type=Path)
    parser.add_argument("--slice", type=Path, default=DEFAULT_SLICE)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    payload = summarize_pair(args.main_dir, args.public_feedback_dir, args.slice)
    print(json.dumps(payload, indent=2, sort_keys=True))
    _print_table(payload)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
