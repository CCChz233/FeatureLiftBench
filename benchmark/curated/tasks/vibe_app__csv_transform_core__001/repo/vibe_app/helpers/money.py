"""Currency helpers."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal


def round_money(value: float, digits: int = 2) -> float:
    quant = Decimal("1").scaleb(-digits)
    return float(Decimal(str(value)).quantize(quant, rounding=ROUND_HALF_UP))


def format_money(value: float, currency: str = "USD") -> str:
    return f"{currency} {round_money(value):.2f}"
