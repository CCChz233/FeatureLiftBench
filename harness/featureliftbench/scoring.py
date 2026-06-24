"""Scoring helpers."""

from __future__ import annotations

from typing import Any


def functional_gate(
    *,
    build_pass: bool,
    test_pass: bool,
    original_import_pass: bool,
) -> float:
    """Return 1.0 only when all functional gates pass."""

    return 1.0 if build_pass and test_pass and original_import_pass else 0.0


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def score_submission(
    *,
    metrics: dict[str, int | float],
    metadata: dict[str, Any],
    functional_gate_score: float,
) -> dict[str, float]:
    """Compute simple pass-plus-extraction-ratio scores."""

    del metadata

    extraction_ratio = _extraction_ratio(metrics)
    if functional_gate_score <= 0:
        return {
            "functional_gate": functional_gate_score,
            "extraction_ratio": round(extraction_ratio, 6),
            "final_score": 0.0,
        }

    final_score = clamp(functional_gate_score * (1.0 - extraction_ratio))

    return {
        "functional_gate": functional_gate_score,
        "extraction_ratio": round(extraction_ratio, 6),
        "final_score": round(final_score, 6),
    }


def _extraction_ratio(metrics: dict[str, int | float]) -> float:
    source_loc = float(metrics.get("source_loc", 0))
    submission_loc = float(metrics.get("loc", 0))
    if source_loc <= 0:
        return 0.0 if submission_loc <= 0 else 1.0
    return max(0.0, submission_loc / source_loc)
