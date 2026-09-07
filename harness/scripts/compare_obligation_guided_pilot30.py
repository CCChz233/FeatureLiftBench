#!/usr/bin/env python3
"""Compare archived Main vs Obligation-Guided on the pilot-30 slice.

Primary metric is evaluator functional_gate. Rescue = Main 0 and OG 1.
Not a Python-150/200 main-table result.
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

from featureliftbench.suite_utils import functional_gate_value

DEFAULT_SLICE = (
    _REPO_ROOT / "harness/config/experiments/obligation_guided_pilot30_v1.txt"
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _task_ids_from_list(path: Path) -> list[str]:
    ids: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        ids.append(line)
    return ids


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


def _audit(suite_dir: Path, task_id: str) -> dict[str, Any]:
    path = suite_dir / task_id / "agent" / "obligation_guided_audit.json"
    if not path.is_file():
        return {}
    try:
        payload = _load_json(path)
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("main_suite", type=Path)
    parser.add_argument("obligation_suite", type=Path)
    parser.add_argument("--task-list", type=Path, default=DEFAULT_SLICE)
    args = parser.parse_args()
    task_ids = _task_ids_from_list(args.task_list)
    if not task_ids:
        print("empty task list", file=sys.stderr)
        return 2
    main_runs = _run_map(args.main_suite)
    og_runs = _run_map(args.obligation_suite)
    rows = []
    rescue = 0
    both_fail = 0
    og_only_fail = 0
    both_pass = 0
    unknown = 0
    for task_id in task_ids:
        main_eval = _eval_result(args.main_suite, task_id)
        og_eval = _eval_result(args.obligation_suite, task_id)
        main_gate = functional_gate_value(main_runs.get(task_id) or {})
        if main_gate is None:
            main_gate = main_eval.get("functional_gate")
        og_gate = functional_gate_value(og_runs.get(task_id) or {})
        if og_gate is None:
            og_gate = og_eval.get("functional_gate")
        main_pass = main_gate == 1.0 or main_gate == 1
        og_pass = og_gate == 1.0 or og_gate == 1
        if main_gate is None or og_gate is None:
            unknown += 1
            pair = "unknown"
        elif not main_pass and og_pass:
            rescue += 1
            pair = "rescue"
        elif main_pass and og_pass:
            both_pass += 1
            pair = "both_pass"
        elif not main_pass and not og_pass:
            both_fail += 1
            pair = "both_fail"
        else:
            og_only_fail += 1
            pair = "regression"
        hidden_flip = (
            main_eval.get("hidden_pass") is False and og_eval.get("hidden_pass") is True
        )
        public_flip = (
            main_eval.get("public_pass") is False and og_eval.get("public_pass") is True
        )
        rows.append(
            {
                "task_id": task_id,
                "pair": pair,
                "main_functional": main_gate,
                "og_functional": og_gate,
                "public_0_to_1": bool(public_flip),
                "hidden_0_to_1": bool(hidden_flip),
                "coverage_complete": _audit(args.obligation_suite, task_id).get(
                    "coverage_complete"
                ),
            }
        )
    payload = {
        "schema_version": "featureliftbench.obligation_guided_pilot30_pair.v1",
        "n": len(task_ids),
        "rescue": rescue,
        "both_fail": both_fail,
        "both_pass": both_pass,
        "regression": og_only_fail,
        "unknown": unknown,
        "kill_if_rescue_le": 3,
        "expand_if_rescue_ge": 8,
        "rows": rows,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    if rescue <= 3:
        print(
            f"stop rule: rescue {rescue} <= 3; do not expand; Discussion negative result",
            file=sys.stderr,
        )
    elif rescue >= 8:
        print(
            f"continue rule candidate: rescue {rescue} >= 8; confirm drift rescues before expanding",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
