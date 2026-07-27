"""Canonical pricing rules engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from vibe_app.helpers.money import round_money
from vibe_app.pricing.discounts import category_multiplier, member_multiplier
from vibe_app.pricing.tiers import tier_multiplier
from vibe_app.state import GLOBAL_STATE


@dataclass
class PricingContext:
    is_member: bool = False
    customer_tier: str | None = None
    config: dict[str, Any] | None = None

    def pricing_section(self) -> dict[str, Any]:
        cfg = self.config or GLOBAL_STATE.get("config", {})
        return cfg.get("pricing", {})


def compute_line_price(
    unit_price: float,
    quantity: int,
    category: str,
    *,
    context: PricingContext | None = None,
) -> float:
    ctx = context or PricingContext()
    pricing_cfg = ctx.pricing_section()
    digits = int(pricing_cfg.get("round_digits", 2))

    subtotal = float(unit_price) * int(quantity)
    subtotal *= category_multiplier(category, pricing_cfg)
    subtotal *= tier_multiplier(int(quantity), list(pricing_cfg.get("tiers", [])))
    subtotal *= member_multiplier(ctx.is_member, pricing_cfg)
    return round_money(subtotal, digits)
