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
if str(_REPO_ROOT / "harness" / "scripts") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "harness" / "scripts"))

from featureliftbench.go_quality import go_no_stub_gate

CALIBRATION_EXT_EPSILON = 0.03


def generate_go_gate_report(task_id: str, *, attempt: int = 1) -> dict[str, Any]:
    review = _REPO_ROOT / "experiments" / "go-pilot" / task_id / "review"
    return _generate_with_review(task_id, review, attempt=attempt)


def _generate_with_review(task_id: str, review: Path, *, attempt: int = 1) -> dict[str, Any]:
    import generate_gate_report as mod

    task_dir = _go_task_dir(task_id)
    quality = go_no_stub_gate(
        task_id,
        task_dir,
        repo_root=_REPO_ROOT,
        oracle_dir=_REPO_ROOT / "benchmark" / "submissions" / task_id / "oracle",
    )

    oracle = mod._eval_gate(mod._load_result(review / "oracle" / "result.json"))
    naive = mod._eval_gate(mod._load_result(review / "naive" / "result.json"))
    copy_all = mod._eval_gate(mod._load_result(review / "copy_all" / "result.json"))

    flash_path = review / "flash" / "run.json"
    if not flash_path.is_file():
        flash_path = review / "flash" / "result.json"
    flash = mod._load_result(flash_path) if flash_path.is_file() else None
    flash_eval = _flash_eval_payload(flash)
    flash_tier = mod._flash_tier(flash)

    g0_validate = mod._log_ok(review / "validate-task.log", ("valid task:",))
    g0_audit = mod._log_ok(review / "audit-output-imports.log", ("[OK]", "0 with L1 gaps", "audit ok"))
    g0_quality = bool(quality["passed"])
    g0 = g0_validate and g0_audit and g0_quality

    blocking: list[str] = []
    gates: dict[str, bool] = {}

    if not g0:
        if not g0_validate:
            blocking.append("G0_validate_task")
        if not g0_audit:
            blocking.append("G0_audit_output_imports")
        if not g0_quality:
            blocking.extend(str(item) for item in quality["blocking_gates"])
    gates["G0_task_shape"] = g0
    gates["G0_no_stub"] = g0_quality

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

    flash_scores = flash_eval.get("scores") or {}
    flash_ext = _float_or_none(flash_scores.get("extraction_ratio"))
    flash_hidden = (flash_eval.get("hidden_tests") or {}).get("passed")
    readiness = _readiness_classification(
        mechanical_pass=g0 and g1 and g2 and g3 and g4,
        flash_tier=flash_tier,
        flash_hidden=flash_hidden,
        flash_ext=flash_ext,
        oracle_ext=oracle_ext,
        copy_ext=copy_ext,
    )

    mechanical_pass = g0 and g1 and g2 and g3 and g4
    if not mechanical_pass:
        decision = "redesign"
    elif flash_tier == "not_run":
        decision = "pending_flash"
    elif flash_tier == "C":
        decision = "redesign"
    elif readiness["readiness"] in {"calibration_pass", "overextract_pass"}:
        decision = "promote_calibration"
    else:
        decision = "paper_ready_hard"

    if decision in {"promote_calibration", "paper_ready_hard"}:
        blocking = [b for b in blocking if b not in ("G5_flash_not_run",)]

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
            "flash_extraction": flash_scores.get("extraction_ratio"),
            "flash_final": flash_scores.get("final_score"),
        },
        "evidence": {
            "oracle_result": f"{review_prefix}/oracle/result.json",
            "naive_result": f"{review_prefix}/naive/result.json",
            "copy_all_result": f"{review_prefix}/copy_all/result.json",
            "flash_run": f"{review_prefix}/flash/run.json" if flash_path.is_file() else None,
        },
        "gates": gates,
        "readiness": readiness,
        "quality": quality,
    }


def _flash_eval_payload(flash: dict[str, Any] | None) -> dict[str, Any]:
    if not flash:
        return {}
    eval_data = flash.get("evaluation") or flash
    if isinstance(eval_data, dict) and eval_data.get("result_json"):
        try:
            eval_path = Path(str(eval_data["result_json"]))
            if eval_path.is_file():
                return json.loads(eval_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    return eval_data if isinstance(eval_data, dict) else {}


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _readiness_classification(
    *,
    mechanical_pass: bool,
    flash_tier: str,
    flash_hidden: Any,
    flash_ext: float | None,
    oracle_ext: float,
    copy_ext: float,
) -> dict[str, Any]:
    if not mechanical_pass:
        return {
            "readiness": "redesign",
            "reason": "mechanical gates did not pass",
        }
    if flash_tier == "not_run":
        return {
            "readiness": "pending_flash",
            "reason": "real agent evidence is missing",
        }
    if flash_tier == "C":
        return {
            "readiness": "redesign",
            "reason": "Flash tier C does not establish useful calibration",
        }
    if flash_hidden is True and flash_ext is not None:
        oracle_delta = abs(flash_ext - oracle_ext)
        copy_delta = copy_ext - flash_ext
        if oracle_delta < CALIBRATION_EXT_EPSILON:
            return {
                "readiness": "calibration_pass",
                "reason": (
                    "Flash passed hidden tests with a footprint indistinguishable "
                    "from oracle; useful as pipeline calibration, not hard paper-ready evidence"
                ),
                "flash_oracle_delta": round(oracle_delta, 6),
                "threshold": CALIBRATION_EXT_EPSILON,
            }
        if copy_ext > 0 and copy_delta >= 0.20:
            return {
                "readiness": "paper_ready_hard",
                "reason": "Flash passed with a compact footprint distinct from copy_all and oracle",
                "flash_oracle_delta": round(oracle_delta, 6),
                "flash_copy_delta": round(copy_delta, 6),
            }
        return {
            "readiness": "overextract_pass",
            "reason": (
                "Flash passed hidden tests but extracted close to copy_all; "
                "useful calibration, not hard paper-ready evidence"
            ),
            "flash_oracle_delta": round(oracle_delta, 6),
            "flash_copy_delta": round(copy_delta, 6),
            "copy_delta_threshold": 0.20,
        }
    if flash_tier == "A":
        return {
            "readiness": "paper_ready_hard",
            "reason": "Flash public-pass/hidden-fail behavior provides hard-task discrimination",
        }
    return {
        "readiness": "paper_ready_hard",
        "reason": "Flash evidence passed the hard-readiness heuristic",
    }


def _go_task_dir(task_id: str) -> Path:
    for parent in ("staging", "tasks", "sanity"):
        candidate = _REPO_ROOT / "benchmark" / "go" / parent / task_id
        if candidate.is_dir():
            return candidate
    return _REPO_ROOT / "benchmark" / "go" / "tasks" / task_id


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
