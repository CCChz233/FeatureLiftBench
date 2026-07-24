"""Constitution API-surface coverage generated from public_spec."""

from featurelifted import (
    parse,
    parsestream,
    sql,
    tokens,
)


def test_required_api_surface():
    assert callable(parse)
    assert callable(parsestream)
    assert sql is not None
    assert tokens is not None
