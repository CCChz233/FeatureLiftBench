#!/usr/bin/env python3
"""Generate gate_report.json from Go pilot review evidence files."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "harness"))

from generate_gate_report import generate_gate_report as _generate_base_report


def generate_go_gate_report(task_id: str, *, attempt: int = 1) -> dict[str, Any]:
    report = _generate_base_report(task_id, attempt=attempt)
    review_prefix = f"experiments/go-pilot/{task_id}/review"
    report["evidence"] = {
        "oracle_result": f"{review_prefix}/oracle/result.json",
        "naive_result": f"{review_prefix}/naive/result.json",
        "copy_all_result": f"{review_prefix}/copy_all/result.json",
        "flash_run": f"{review_prefix}/flash/run.json",
    }
    return report


def _patch_review_root(task_id: str) -> None:
    import generate_gate_report as mod

    review = _REPO_ROOT / "experiments" / "go-pilot" / task_id / "review"
    mod._REPO_ROOT = _REPO_ROOT  # noqa: SLF001

    original = mod.generate_gate_report

    def wrapped(tid: str, *, attempt: int = 1) -> dict[str, Any]:
        old_batch1 = _REPO_ROOT / "experiments" / "batch1" / tid / "review"
        # Monkey-patch review path by temporarily symlink-style: copy loader logic
        review_go = _REPO_ROOT / "experiments" / "go-pilot" / tid / "review"
        return _generate_with_review(tid, review_go, attempt=attempt)

    mod.generate_gate_report = wrapped  # type: ignore[method-assign]


def _generate_with_review(task_id: str, review: Path, *, attempt: int = 1) -> dict[str, Any]:
    import generate_gate_report as mod

    oracle = mod._eval_gate(mod._load_result(review / "oracle" / "result.json"))
    naive = mod._eval_gate(mod._load_result(review / "naive" / "result.json"))
    copy_all = mod._eval_gate(mod._load_result(review / "copy_all" / "result.json"))

    flash_path = review / "flash" / "run.json"
    if not flash_path.is_file():
        flash_path = review / "flash" / "result.json"
    flash = mod._load_result(flash_path) if flash_path.is_file() else None
    flash_tier = mod._flash_tier(flash)

    g0_validate = mod._log_ok(review / "validate-task.log", ("valid task:",))
    g0_audit = mod._log_ok(review / "audit-output-imports.log", ("[OK]", "0 with L1 gaps", "audit ok"))
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
        and mod.G1_EXT_MIN <= float(oracle["extraction"]) <= mod.G1_EXT_MAX
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
        and float(naive["extraction"]) <= mod.G2_EXT_MAX
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
        and delta >= mod.G3_DELTA_MIN
        and (
            copy_ext >= mod.G3_EXT_MIN
            or (copy_ext >= mod.G3_EXT_TRIM_MIN and delta >= mod.G3_DELTA_TRIM_MIN)
        )
    )
    if copy_all["present"] and not g3:
        blocking.append("G3_copy_all")
    gates["G3_copy_all"] = g3

    g4 = mod._probe_ok(review / "module-probes.log")
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
    else:
        decision = "promote"

    if decision == "promote":
        blocking = [b for b in blocking if b not in ("G5_flash_not_run",)]

    flash_scores = (flash or {}).get("evaluation", flash) or {}
    flash_metrics = flash_scores.get("scores") or {}
    review_prefix = f"experiments/go-pilot/{task_id}/review"

    return {
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
            "oracle_result": f"{review_prefix}/oracle/result.json",
            "naive_result": f"{review_prefix}/naive/result.json",
            "copy_all_result": f"{review_prefix}/copy_all/result.json",
            "flash_run": f"{review_prefix}/flash/run.json" if flash_path.is_file() else None,
        },
        "gates": gates,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_ids", nargs="+", help="Go task IDs")
    args = parser.parse_args()

    for task_id in args.task_ids:
        report = _generate_with_review(task_id, _REPO_ROOT / "experiments" / "go-pilot" / task_id / "review")
        out = _REPO_ROOT / "experiments" / "go-pilot" / task_id / "review" / "gate_report.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(
            f"{task_id}: decision={report['decision']} "
            f"flash={report['flash_tier']} blocking={report['blocking_gates']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
