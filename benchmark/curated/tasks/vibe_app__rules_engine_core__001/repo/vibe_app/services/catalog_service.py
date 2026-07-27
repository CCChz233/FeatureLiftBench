"""Catalog lookups — not needed for benchmark APIs."""

from __future__ import annotations

from vibe_app.models.product import Product


def sample_catalog() -> list[Product]:
    return [
        Product("A100", "Widget", "electronics", 9.99),
        Product("B200", "Notebook", "books", 4.50),
    ]
