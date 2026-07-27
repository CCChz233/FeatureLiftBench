"""Quantity tier lookup."""

from __future__ import annotations

from typing import Any


def tier_multiplier(quantity: int, tiers: list[dict[str, Any]]) -> float:
    applicable = 1.0
    for tier in sorted(tiers, key=lambda item: int(item.get("min_qty", 0))):
        min_qty = int(tier.get("min_qty", 0))
        if quantity >= min_qty:
            applicable = float(tier.get("multiplier", 1.0))
    return applicable
