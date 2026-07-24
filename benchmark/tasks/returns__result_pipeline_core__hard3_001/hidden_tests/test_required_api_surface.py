"""Constitution API-surface coverage generated from public_spec."""

from featurelifted import (
    Result,
    Success,
    Failure,
    safe,
)


def test_required_api_surface():
    assert isinstance(Result, type)
    assert isinstance(Success, type)
    assert hasattr(Success, 'map')
    assert Success is not None
    assert isinstance(Failure, type)
    assert Failure is not None
    assert callable(safe)
