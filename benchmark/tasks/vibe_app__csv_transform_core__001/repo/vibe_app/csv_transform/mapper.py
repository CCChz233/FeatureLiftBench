"""Header and field normalization."""

from __future__ import annotations

from typing import Any

from vibe_app.helpers.strings import normalize_header


def normalize_row_keys(row: dict[str, Any]) -> dict[str, Any]:
    return {normalize_header(str(key)): value for key, value in row.items()}


def coerce_numeric_fields(row: dict[str, Any]) -> dict[str, Any]:
    result = dict(row)
    if "quantity" in result:
        result["quantity"] = int(str(result["quantity"]).strip() or "0")
    if "unit_price" in result:
        result["unit_price"] = float(str(result["unit_price"]).strip() or "0")
    return result
