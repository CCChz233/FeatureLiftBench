"""Category and membership adjustments."""

from __future__ import annotations

from typing import Any


def category_multiplier(category: str, pricing_cfg: dict[str, Any]) -> float:
    categories = pricing_cfg.get("categories", {})
    return float(categories.get(category, categories.get("default", 1.0)))


def member_multiplier(is_member: bool, pricing_cfg: dict[str, Any]) -> float:
    if not is_member:
        return 1.0
    members = pricing_cfg.get("members", {})
    return float(members.get("discount", 1.0))
