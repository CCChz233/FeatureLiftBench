"""Constitution API-surface coverage generated from public_spec."""

from featurelifted import (
    parse,
    parsestream,
    split,
    sql,
    tokens,
)


def test_required_api_surface():
    assert callable(parse)
    assert callable(parsestream)
    assert callable(split)
    assert sql is not None
    assert tokens is not None
