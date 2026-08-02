from __future__ import annotations

import re
from pathlib import Path

from featurelifted import exp, parse, parse_one, transpile


def test_parse_multiple() -> None:
    nodes = parse("SELECT 1; SELECT 2")
    assert len(nodes) == 2
    assert all(isinstance(n, exp.Select) for n in nodes)


def test_mysql_dialect_backticks() -> None:
    node = parse_one("SELECT `a` FROM t", read="mysql")
    assert isinstance(node, exp.Select)
    sql = node.sql(dialect="mysql")
    assert "a" in sql


def test_pretty_sql() -> None:
    node = parse_one("SELECT a, b FROM t")
    sql = node.sql(pretty=True)
    assert "SELECT" in sql and "FROM" in sql


def test_transpile_mysql_to_sqlite() -> None:
    out = transpile("SELECT `x` FROM t", read="mysql", write="sqlite")
    assert isinstance(out, list) and out and "x" in out[0]


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\s*(?:from sqlglot\b|import sqlglot\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
