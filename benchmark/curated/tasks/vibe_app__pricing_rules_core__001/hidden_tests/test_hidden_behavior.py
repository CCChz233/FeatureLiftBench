from __future__ import annotations

from featurelifted import PricingContext
from featurelifted import compute_line_price


def test_tier_boundary_uses_highest_applicable() -> None:
    cfg = {
        "pricing": {
            "round_digits": 2,
            "categories": {"default": 1.0},
            "tiers": [
                {"min_qty": 5, "multiplier": 0.98},
                {"min_qty": 10, "multiplier": 0.95},
                {"min_qty": 50, "multiplier": 0.90},
            ],
            "members": {"discount": 1.0},
        }
    }
    ctx = PricingContext(config=cfg)

    assert compute_line_price(2.0, 9, "default", context=ctx) == 17.64
    assert compute_line_price(2.0, 10, "default", context=ctx) == 19.0
    assert compute_line_price(2.0, 50, "default", context=ctx) == 90.0


def test_unknown_category_falls_back_to_default() -> None:
    cfg = {
        "pricing": {
            "round_digits": 2,
            "categories": {"default": 1.0},
            "tiers": [],
            "members": {"discount": 1.0},
        }
    }
    ctx = PricingContext(config=cfg)

    assert compute_line_price(3.33, 3, "unknown", context=ctx) == 9.99
