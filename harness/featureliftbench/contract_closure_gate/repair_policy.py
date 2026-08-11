"""Auditable bounded-repair policies for Contract Closure Gate experiments."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import DEFAULT_LITE_MAX_MISSING_APIS
from .common import DEFAULT_LITE_MAX_REPAIR_FAILURES
from .common import LITE_POLICY_VERSION
from .common import LITE_V1_POLICY_VERSION
from .common import V3_POLICY_VERSION

_LOCAL_REPAIR_CATEGORIES = frozenset({"api", "signature", "dependency"})
_V3_REPAIR_CATEGORIES = _LOCAL_REPAIR_CATEGORIES | {"behavior"}


def _actionable_behavior_failure(item: dict[str, Any]) -> bool:
    if item.get("category") != "behavior" or item.get("status") != "fail":
        return False
    return str(item.get("message") or "").startswith(
        (
            "featurelifted observation differs from stable upstream",
            "featurelifted case failed:",
            "direct assertion failed:",
        )
    )


def decide_repair(
    workspace_dir: str | Path,
    check_result: dict[str, Any],
    *,
    lite: bool,
    frozen_v1: bool = False,
    v3: bool = False,
) -> dict[str, Any]:
    """Return a deterministic decision without consulting evaluator information."""

    requested = bool(check_result.get("repair_needed"))
    decision: dict[str, Any] = {
        "policy_version": (
            V3_POLICY_VERSION
            if v3
            else LITE_V1_POLICY_VERSION
            if frozen_v1
            else LITE_POLICY_VERSION
            if lite
            else "contract_closure_gate.v1"
        ),
        "requested": requested,
        "eligible": requested,
        "reason": "checker did not request repair" if not requested else "repair requested",
    }
    if not requested or frozen_v1 or not (lite or v3):
        return decision

    workspace = Path(workspace_dir).resolve()
    python_files = sorted((workspace / "submission").rglob("*.py"))
    if not python_files:
        return {
            **decision,
            "eligible": False,
            "reason": "empty submission is not eligible for bounded local repair",
            "python_file_count": 0,
        }

    failed = [
        item
        for item in check_result.get("checks", [])
        if isinstance(item, dict)
        and item.get("status") == "fail"
        and item.get("severity") == "hard"
    ]
    if v3:
        failed.extend(
            item
            for item in check_result.get("checks", [])
            if isinstance(item, dict) and _actionable_behavior_failure(item)
        )
    categories = sorted({str(item.get("category") or "") for item in failed})
    decision.update(
        {
            "python_file_count": len(python_files),
            "hard_failure_count": len(failed),
            "failure_categories": categories,
        }
    )
    if not failed:
        return {
            **decision,
            "eligible": False,
            "reason": "no hard local defect is available for repair",
        }
    if any(item.get("id") == "submission.compile" for item in failed):
        return {
            **decision,
            "eligible": False,
            "reason": "non-compiling submissions are too broad for bounded repair",
        }
    allowed_categories = _V3_REPAIR_CATEGORIES if v3 else _LOCAL_REPAIR_CATEGORIES
    if any(category not in allowed_categories for category in categories):
        return {
            **decision,
            "eligible": False,
            "reason": "failure category is not eligible for bounded local repair",
        }
    if len(failed) > DEFAULT_LITE_MAX_REPAIR_FAILURES:
        return {
            **decision,
            "eligible": False,
            "reason": (
                f"{len(failed)} actionable failures exceed the bounded limit of "
                f"{DEFAULT_LITE_MAX_REPAIR_FAILURES}"
            ),
        }
    missing_api_count = sum(
        item.get("category") == "api" and item.get("status") == "fail"
        for item in failed
    )
    decision["missing_api_count"] = missing_api_count
    if missing_api_count > DEFAULT_LITE_MAX_MISSING_APIS:
        return {
            **decision,
            "eligible": False,
            "reason": (
                f"{missing_api_count} missing APIs exceed the bounded limit of "
                f"{DEFAULT_LITE_MAX_MISSING_APIS}"
            ),
        }
    return {
        **decision,
        "eligible": True,
        "reason": (
            "small, concrete public-behavior mismatch"
            if v3 and "behavior" in categories
            else "small, local, structurally repairable public-contract gap"
        ),
    }
