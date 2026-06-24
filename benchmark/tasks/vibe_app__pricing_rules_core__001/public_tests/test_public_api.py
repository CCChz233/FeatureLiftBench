from __future__ import annotations

from featurelifted import PricingContext
from featurelifted import compute_line_price


def _pricing_cfg() -> dict:
    return {
        "pricing": {
            "round_digits": 2,
            "categories": {"books": 0.95, "electronics": 1.05, "default": 1.0},
            "tiers": [
                {"min_qty": 5, "multiplier": 0.98},
                {"min_qty": 10, "multiplier": 0.95},
            ],
            "members": {"discount": 0.90},
        }
    }


def test_category_multiplier_applied() -> None:
    ctx = PricingContext(config=_pricing_cfg())

    assert compute_line_price(10.0, 2, "books", context=ctx) == 19.0


def test_member_discount_with_tier() -> None:
    ctx = PricingContext(is_member=True, config=_pricing_cfg())

    assert compute_line_price(5.0, 10, "electronics", context=ctx) == 44.89
