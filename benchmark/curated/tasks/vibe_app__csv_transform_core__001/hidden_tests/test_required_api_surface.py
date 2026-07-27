"""Constitution API-surface coverage generated from public_spec."""

from featurelifted import (
    TransformOptions,
    transform_csv,
)


def test_required_api_surface():
    assert isinstance(TransformOptions, type)
    assert callable(transform_csv)
