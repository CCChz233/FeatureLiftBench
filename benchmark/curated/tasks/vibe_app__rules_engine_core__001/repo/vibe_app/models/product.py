"""Product model clutter."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Product:
    sku: str
    name: str
    category: str
    unit_price: float
