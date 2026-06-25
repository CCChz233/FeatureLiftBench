"""Order totals using pricing rules via utils indirection."""

from __future__ import annotations

from vibe_app.pricing.rules import PricingContext
from vibe_app.utils import compute_line_price


def order_line_total(unit_price: float, quantity: int, category: str, *, member: bool = False) -> float:
    ctx = PricingContext(is_member=member)
    return compute_line_price(unit_price, quantity, category, context=ctx)
