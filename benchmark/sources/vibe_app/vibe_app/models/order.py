"""Order model clutter."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class OrderLine:
    sku: str
    quantity: int
    category: str
    unit_price: float


@dataclass
class Order:
    lines: list[OrderLine] = field(default_factory=list)
