"""Constitution API-surface coverage generated from public_spec."""

from featurelifted import (
    define,
    field,
    validate,
    validators,
)


def test_required_api_surface():
    assert callable(define)
    assert callable(field)
    assert callable(validate)
    assert validators is not None
