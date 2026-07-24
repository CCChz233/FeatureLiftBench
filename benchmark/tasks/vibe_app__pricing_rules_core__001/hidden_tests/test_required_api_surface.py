"""Constitution API-surface coverage generated from public_spec."""

from featurelifted import (
    PricingContext,
    compute_line_price,
)


def test_required_api_surface():
    assert isinstance(PricingContext, type)
    assert PricingContext is not None
    assert callable(compute_line_price)
