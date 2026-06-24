"""Dedupe by sku — last row wins."""

from __future__ import annotations

from typing import Any


def dedupe_by_sku(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    for row in rows:
        seen[str(row.get("sku", ""))] = row
    return [seen[key] for key in sorted(seen)]
