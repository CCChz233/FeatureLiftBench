"""Old pricing path kept for backwards compat — wrong semantics."""

from __future__ import annotations


def legacy_line_total(unit_price: float, quantity: int) -> float:
    return round(unit_price * quantity, 3)
