"""Row filtering helpers."""

from __future__ import annotations

from typing import Any


def row_is_valid(row: dict[str, Any]) -> bool:
    sku = str(row.get("sku", "")).strip()
    qty = row.get("quantity", 0)
    try:
        qty_val = int(qty)
    except (TypeError, ValueError):
        return False
    return bool(sku) and qty_val > 0


def filter_by_min_quantity(row: dict[str, Any], minimum: int) -> bool:
    try:
        return int(row.get("quantity", 0)) >= minimum
    except (TypeError, ValueError):
        return False
