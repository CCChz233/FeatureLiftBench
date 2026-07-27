"""Rule condition matching."""

from __future__ import annotations

from typing import Any


def match_condition(condition: dict[str, Any], facts: dict[str, Any]) -> bool:
    """Return whether a single condition matches the given facts."""
    field = condition.get("field")
    if field is None:
        return False

    op = condition.get("op", "eq")
    expected = condition.get("value")
    actual = facts.get(field)

    if op == "eq":
        return actual == expected
    if op == "neq":
        return actual != expected
    if op == "gt":
        return actual is not None and actual > expected
    if op == "gte":
        return actual is not None and actual >= expected
    if op == "lt":
        return actual is not None and actual < expected
    if op == "lte":
        return actual is not None and actual <= expected
    if op == "in":
        return actual in expected
    if op == "contains":
        return expected in (actual or [])
    return False
