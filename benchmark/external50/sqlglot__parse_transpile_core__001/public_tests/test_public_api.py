from __future__ import annotations

from featurelifted import exp, parse_one, transpile
from featurelifted.errors import ParseError


def test_parse_one_select() -> None:
    node = parse_one("SELECT a FROM t")
    assert isinstance(node, exp.Select)
    rendered = node.sql()
    assert rendered == "SELECT a FROM t"


def test_transpile_sqlite_to_postgres() -> None:
    out = transpile("SELECT a FROM t", read="sqlite", write="postgres")
    assert out == ["SELECT a FROM t"]


def test_parse_error() -> None:
    try:
        parse_one("SELECT FROM")
        assert False
    except ParseError:
        pass
