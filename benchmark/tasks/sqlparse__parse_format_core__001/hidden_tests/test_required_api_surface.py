"""Constitution API-surface coverage generated from public_spec."""

from featurelifted import (
    parse,
    parsestream,
    split,
    format,
    sql,
    tokens,
    exceptions,
)


def test_required_api_surface():
    assert callable(parse)
    assert callable(parsestream)
    assert callable(split)
    assert callable(format)
    assert sql is not None
    assert tokens is not None
    assert exceptions is not None
    assert issubclass(getattr(exceptions, 'SQLParseError'), BaseException)
