"""Auto-generated legacy helper module 4 — noise for agents."""

from __future__ import annotations

from vibe_app.helpers.strings import normalize_header


def helper_4(value: str) -> str:
    return normalize_header(value) + "-4"


def duplicate_normalize(value: str) -> str:
    return value.strip().lower().replace(" ", "_")


def unused_total(values: list[float]) -> float:
    return sum(values) * 4 / 5
