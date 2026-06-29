#!/usr/bin/env python3
"""Generate gate_report.json from batch-1 review evidence files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "harness"))

G1_EXT_MIN = 0.09
G1_EXT_MAX = 0.60
G2_EXT_MAX = 0.11
G3_EXT_MIN = 0.85
G3_EXT_TRIM_MIN = 0.70
G3_DELTA_MIN = 0.20
G3_DELTA_TRIM_MIN = 0.30


def _load_result(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _log_ok(path: Path, success_markers: tuple[str, ...]) -> bool:
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    if any(marker in text for marker in success_markers):
        return True
    return path.stat().st_size > 0 and "error" not in text.lower()[:200]


def _probe_ok(path: Path) -> bool:
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    if re.search(r"Oracle probe verification:\s*\d+ passed,\s*0 failed", text):
        return True
    if "0 failed" in text and "probe verification" in text.lower():
        return True
    return False


def _eval_gate(result: dict[str, Any] | None) -> dict[str, Any]:
    if result is None:
        return {
            "present": False,
            "status_passed": False,
            "public_pass": False,
            "hidden_pass": False,
            "functional_gate": 0.0,
            "extraction": None,
            "final_score": None,
        }
    scores = result.get("scores", {})
    public = result.get("public_tests", {})
    hidden = result.get("hidden_tests", {})
    return {
        "present": True,
        "status_passed": result.get("status") == "passed",
        "public_pass": bool(public.get("passed")),
        "hidden_pass": bool(hidden.get("passed")),
        "functional_gate": float(scores.get("functional_gate", 0.0)),
        "extraction": scores.get("extraction_ratio"),
        "final_score": scores.get("final_score"),
    }


def _flash_tier(flash: dict[str, Any] | None) -> str:
    if flash is None:
        return "not_run"
    eval_data = flash.get("evaluation") or flash
    if isinstance(eval_data, dict) and eval_data.get("result_json"):
        try:
            eval_path = Path(str(eval_data["result_json"]))
            if eval_path.is_file():
                eval_data = json.loads(eval_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    scores = eval_data.get("scores") or flash.get("scores") or {}
    ext = scores.get("extraction_ratio")
    functional = scores.get("functional_gate", flash.get("functional_gate"))
    hidden = (eval_data.get("hidden_tests") or flash.get("hidden_tests") or {}).get("passed")
    public = (eval_data.get("public_tests") or flash.get("public_tests") or {}).get("passed")

    if functional == 0.0 and public and hidden is False:
        return "A"
    if functional == 1.0 and ext is not None and ext >= 0.45:
        return "B"
    if functional == 1.0 and ext is not None and ext < 0.15:
        return "C"
    if functional == 1.0:
        return "B"
    return "C"


def generate_gate_report(task_id: str, *, attempt: int = 1) -> dict[str, Any]:
    review = _REPO_ROOT / "experiments" / "batch1" / task_id / "review"
    oracle = _eval_gate(_load_result(review / "oracle" / "result.json"))
    naive = _eval_gate(_load_result(review / "naive" / "result.json"))
    copy_all = _eval_gate(_load_result(review / "copy_all" / "result.json"))

    flash_path = review / "flash" / "run.json"
    if not flash_path.is_file():
        flash_path = review / "flash" / "result.json"
    flash = _load_result(flash_path) if flash_path.is_file() else None
    flash_tier = _flash_tier(flash)

    g0_validate = _log_ok(review / "validate-task.log", ("valid task:",))
    g0_audit = _log_ok(review / "audit-output-imports.log", ("[OK]", "0 with L1 gaps"))
    g0 = g0_validate and g0_audit

    blocking: list[str] = []
    gates: dict[str, bool] = {}

    if not g0:
        if not g0_validate:
            blocking.append("G0_validate_task")
        if not g0_audit:
            blocking.append("G0_audit_output_imports")
    gates["G0_task_shape"] = g0

    g1 = (
        oracle["present"]
        and oracle["status_passed"]
        and oracle["public_pass"]
        and oracle["hidden_pass"]
        and oracle["functional_gate"] == 1.0
        and oracle["extraction"] is not None
        and G1_EXT_MIN <= float(oracle["extraction"]) <= G1_EXT_MAX
    )
    if oracle["present"] and not g1:
        blocking.append("G1_oracle")
    gates["G1_oracle"] = g1

    g2 = (
        naive["present"]
        and naive["public_pass"]
        and not naive["hidden_pass"]
        and naive["functional_gate"] == 0.0
        and naive["extraction"] is not None
        and float(naive["extraction"]) <= G2_EXT_MAX
    )
    if naive["present"] and not g2:
        blocking.append("G2_naive")
    gates["G2_naive"] = g2

    oracle_ext = float(oracle["extraction"]) if oracle["extraction"] is not None else 0.0
    copy_ext = float(copy_all["extraction"]) if copy_all["extraction"] is not None else 0.0
    delta = copy_ext - oracle_ext

    g3 = (
        copy_all["present"]
        and copy_all["status_passed"]
        and copy_all["public_pass"]
        and copy_all["hidden_pass"]
        and copy_all["functional_gate"] == 1.0
        and copy_all["extraction"] is not None
        and delta >= G3_DELTA_MIN
        and (
            copy_ext >= G3_EXT_MIN
            or (copy_ext >= G3_EXT_TRIM_MIN and delta >= G3_DELTA_TRIM_MIN)
        )
    )
    if copy_all["present"] and not g3:
        blocking.append("G3_copy_all")
    gates["G3_copy_all"] = g3

    g4 = _probe_ok(review / "module-probes.log")
    if not g4:
        blocking.append("G4_probes")
    gates["G4_probes"] = g4

    g5 = flash_tier in ("A", "B")
    if flash_tier == "not_run":
        blocking.append("G5_flash_not_run")
    elif flash_tier == "C":
        blocking.append("G5_flash_tier_C")
    gates["G5_flash"] = g5

    mechanical_pass = g0 and g1 and g2 and g3 and g4
    if not mechanical_pass:
        decision = "redesign"
    elif flash_tier == "not_run":
        decision = "pending_flash"
    elif flash_tier == "C":
        decision = "redesign"
    elif flash_tier == "B":
        decision = "promote"
    else:
        decision = "promote"

    # B-tier promotes per exception workflow; drop flash-not-run from blocking when promoting
    if decision == "promote":
        blocking = [b for b in blocking if b not in ("G5_flash_not_run",)]

    flash_scores = (flash or {}).get("evaluation", flash) or {}
    flash_metrics = flash_scores.get("scores") or {}

    report: dict[str, Any] = {
        "task_id": task_id,
        "attempt": attempt,
        "decision": decision,
        "flash_tier": flash_tier,
        "blocking_gates": sorted(set(blocking)),
        "metrics": {
            "oracle_extraction": oracle["extraction"],
            "oracle_final": oracle["final_score"],
            "naive_extraction": naive["extraction"],
            "copy_all_extraction": copy_all["extraction"],
            "copy_all_delta_vs_oracle": round(delta, 6) if copy_all["extraction"] is not None else None,
            "flash_extraction": flash_metrics.get("extraction_ratio"),
            "flash_final": flash_metrics.get("final_score"),
        },
        "evidence": {
            "oracle_result": f"experiments/batch1/{task_id}/review/oracle/result.json",
            "naive_result": f"experiments/batch1/{task_id}/review/naive/result.json",
            "copy_all_result": f"experiments/batch1/{task_id}/review/copy_all/result.json",
            "flash_run": (
                f"experiments/batch1/{task_id}/review/flash/run.json"
                if flash_path.is_file()
                else None
            ),
        },
        "gates": gates,
    }
    return report


def list_batch1_task_ids() -> list[str]:
    tasks_dir = _REPO_ROOT / "benchmark" / "tasks"
    ids: list[str] = []
    for path in sorted(tasks_dir.iterdir()):
        meta = path / "metadata.json"
        if not meta.is_file():
            continue
        data = json.loads(meta.read_text(encoding="utf-8"))
        tags = data.get("tags") or []
        if "batch-1" in tags:
            ids.append(path.name)
    return ids


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_ids", nargs="*", help="Task IDs (default: all batch-1)")
    parser.add_argument("--all-batch1", action="store_true", help="Generate for all batch-1 tasks")
    parser.add_argument("--write", action="store_true", default=True)
    args = parser.parse_args()

    if args.all_batch1 or not args.task_ids:
        task_ids = list_batch1_task_ids()
    else:
        task_ids = args.task_ids

    for task_id in task_ids:
        report = generate_gate_report(task_id)
        out = _REPO_ROOT / "experiments" / "batch1" / task_id / "review" / "gate_report.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(
            f"{task_id}: decision={report['decision']} "
            f"flash={report['flash_tier']} blocking={report['blocking_gates']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
