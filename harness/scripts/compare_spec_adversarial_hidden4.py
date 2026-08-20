#!/usr/bin/env python3
"""Compare same-day Spec-adversarial Main vs treatment on Hidden-4.

Primary metric is evaluator functional_gate. Kill criterion is Hidden 0→1
count vs same-day Main. Not a Python-200 main-table result.
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
    _REPO_ROOT / "harness/config/experiments/spec_adversarial_hidden4_v1.txt"
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


def summarize_pair(main_dir: Path, treatment_dir: Path, task_list: Path) -> dict[str, Any]:
    expected = _task_ids_from_list(task_list)
    main_runs = _run_map(main_dir)
    treatment_runs = _run_map(treatment_dir)
    task_ids = expected or sorted(set(main_runs) | set(treatment_runs))

    rows: list[dict[str, Any]] = []
    hidden_0_to_1: list[str] = []
    functional_0_to_1: list[str] = []
    integrity = {
        "main_not_mounted": 0,
        "treatment_not_mounted": 0,
        "expected_n": len(expected),
        "task_set_match": set(main_runs.keys()) == set(treatment_runs.keys()),
    }

    for task_id in task_ids:
        main_eval = _eval_result(main_dir, task_id)
        treatment_eval = _eval_result(treatment_dir, task_id)
        main_mount = _mounted(main_dir, task_id)
        treatment_mount = _mounted(treatment_dir, task_id)
        if main_mount is False:
            integrity["main_not_mounted"] += 1
        if treatment_mount is False:
            integrity["treatment_not_mounted"] += 1
        main_gate = _bool01(
            main_eval["functional_gate"]
            if main_eval["available"]
            else functional_gate_value(main_runs.get(task_id) or {})
        )
        treatment_gate = _bool01(
            treatment_eval["functional_gate"]
            if treatment_eval["available"]
            else functional_gate_value(treatment_runs.get(task_id) or {})
        )
        main_hidden = _bool01(main_eval["hidden_pass"])
        treatment_hidden = _bool01(treatment_eval["hidden_pass"])
        main_public = _bool01(main_eval["public_pass"])
        treatment_public = _bool01(treatment_eval["public_pass"])
        hidden_flip = _flip(main_hidden, treatment_hidden)
        gate_flip = _flip(main_gate, treatment_gate)
        if hidden_flip == "0_to_1":
            hidden_0_to_1.append(task_id)
        if gate_flip == "0_to_1":
            functional_0_to_1.append(task_id)
        main_usage = effective_agent_usage_for_run(main_runs.get(task_id) or {})
        treatment_usage = effective_agent_usage_for_run(treatment_runs.get(task_id) or {})
        rows.append(
            {
                "task_id": task_id,
                "main_functional_gate": main_gate,
                "treatment_functional_gate": treatment_gate,
                "main_public": main_public,
                "treatment_public": treatment_public,
                "main_hidden": main_hidden,
                "treatment_hidden": treatment_hidden,
                "hidden_flip": hidden_flip,
                "functional_flip": gate_flip,
                "main_public_tests_mounted": main_mount,
                "treatment_public_tests_mounted": treatment_mount,
                "main_prompt_tokens": int(main_usage.get("prompt_tokens") or 0),
                "treatment_prompt_tokens": int(treatment_usage.get("prompt_tokens") or 0),
            }
        )

    main_pass = sum(row["main_functional_gate"] == 1 for row in rows)
    treatment_pass = sum(row["treatment_functional_gate"] == 1 for row in rows)
    n = len(rows)
    hidden_flip_n = len(hidden_0_to_1)
    decision = "kill" if hidden_flip_n == 0 else ("keep_investigating" if hidden_flip_n >= 2 else "borderline")
    return {
        "schema_version": "featureliftbench.spec_adversarial_hidden4_pair.v1",
        "main_dir": str(main_dir),
        "treatment_dir": str(treatment_dir),
        "task_list": str(task_list),
        "n": n,
        "functional_passed": {
            "main": main_pass,
            "treatment": treatment_pass,
            "delta": treatment_pass - main_pass,
        },
        "hidden_0_to_1": {
            "count": hidden_flip_n,
            "tasks": hidden_0_to_1,
        },
        "functional_0_to_1": functional_0_to_1,
        "decision": decision,
        "integrity": integrity,
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("main_dir", type=Path)
    parser.add_argument("treatment_dir", type=Path)
    parser.add_argument("--task-list", type=Path, default=DEFAULT_SLICE)
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args()
    summary = summarize_pair(args.main_dir, args.treatment_dir, args.task_list)
    text = json.dumps(summary, indent=2, sort_keys=False)
    print(text)
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    print(
        f"\nScreen: Hidden 0→1 = {summary['hidden_0_to_1']['count']}/{summary['n']}; "
        f"decision={summary['decision']}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
