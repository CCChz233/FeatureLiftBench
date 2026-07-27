"""Reporting clutter using wrong pricing helper."""

from __future__ import annotations

from vibe_app.utils import calc_price_v1


def quick_report_total(unit_price: float, quantity: int, category: str) -> float:
    return calc_price_v1(unit_price, quantity, category)
