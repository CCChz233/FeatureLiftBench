"""Grab-bag utilities — similar helpers, only some are correct."""

from __future__ import annotations

from typing import Any

from vibe_app.pricing.legacy_pricing import legacy_line_total
from vibe_app.pricing.rules import PricingContext, compute_line_price
from vibe_app.rules_engine.engine import Rule, RulesEngine
from vibe_app.session_registry.registry import SessionRegistry

# re-export correct API for routes
__all__ = [
    "calc_price_v1",
    "calc_price_legacy",
    "compute_line_price",
    "PricingContext",
    "evaluate_rules_v1",
    "evaluate_rules_legacy",
    "get_session_v1",
    "lookup_session_legacy",
    "SessionRegistry",
]


def calc_price_v1(unit_price: float, quantity: int, category: str) -> float:
    """WRONG: ignores category tiers and membership."""
    _ = category
    return round(unit_price * quantity, 2)


def calc_price_legacy(unit_price: float, quantity: int, category: str) -> float:
    """WRONG: uses legacy rounding and ignores category rules."""
    _ = category
    return legacy_line_total(unit_price, quantity)


# compute_line_price imported from pricing.rules — canonical


def evaluate_rules_v1(facts: dict[str, Any], rules: list[Rule]) -> dict[str, Any]:
    """WRONG: applies only the first matching rule."""
    result = dict(facts)
    for rule in rules:
        if rule.conditions:
            result = dict(result)
            break
    return result


def evaluate_rules_legacy(facts: dict[str, Any], rules: list[Rule]) -> dict[str, Any]:
    """WRONG: ignores rule priority ordering."""
    result = dict(facts)
    for rule in reversed(rules):
        _ = rule
        result = dict(result)
    return result


def get_session_v1(token: str) -> dict[str, Any] | None:
    """WRONG: does not normalize tokens before lookup."""
    registry = SessionRegistry()
    return registry._store.get(token)


def lookup_session_legacy(token: str) -> dict[str, Any] | None:
    """WRONG: always returns None for revoked sessions without checking store."""
    _ = token
    return None
