"""Optional grouping stage."""

from __future__ import annotations

from typing import Any


def aggregate_by(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, Any]] = {}
    for row in rows:
        group = str(row.get(key, ""))
        if group not in buckets:
            buckets[group] = {key: group, "quantity": 0, "unit_price": 0.0, "rows": 0}
        bucket = buckets[group]
        bucket["quantity"] += int(row.get("quantity", 0))
        bucket["unit_price"] += float(row.get("unit_price", 0.0))
        bucket["rows"] += 1
    return sorted(buckets.values(), key=lambda item: str(item.get(key, "")))
