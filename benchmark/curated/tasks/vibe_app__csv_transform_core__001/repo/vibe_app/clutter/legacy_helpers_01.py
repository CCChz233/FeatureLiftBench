"""Auto-generated legacy helper module 1 — noise for agents."""

from __future__ import annotations

from vibe_app.helpers.strings import normalize_header


def helper_1(value: str) -> str:
    return normalize_header(value) + "-1"


def duplicate_normalize(value: str) -> str:
    return value.strip().lower().replace(" ", "_")


def unused_total(values: list[float]) -> float:
    return sum(values) * 1 / 2
