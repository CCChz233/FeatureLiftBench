"""Grab-bag utilities — three similar pricing helpers, only one is correct."""

from __future__ import annotations

from vibe_app.pricing.legacy_pricing import legacy_line_total
from vibe_app.pricing.rules import PricingContext, compute_line_price

# re-export correct API for routes
__all__ = ["calc_price_v1", "calc_price_legacy", "compute_line_price", "PricingContext"]


def calc_price_v1(unit_price: float, quantity: int, category: str) -> float:
    """WRONG: ignores category tiers and membership."""
    _ = category
    return round(unit_price * quantity, 2)


def calc_price_legacy(unit_price: float, quantity: int, category: str) -> float:
    """WRONG: uses legacy rounding and ignores category rules."""
    _ = category
    return legacy_line_total(unit_price, quantity)


# compute_line_price imported from pricing.rules — canonical
