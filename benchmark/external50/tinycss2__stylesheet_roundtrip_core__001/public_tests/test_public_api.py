from __future__ import annotations

from featurelifted import parse_stylesheet, serialize
from featurelifted.ast import AtRule, QualifiedRule


def test_parse_qualified_rule() -> None:
    nodes = [n for n in parse_stylesheet("div { color: red }") if isinstance(n, QualifiedRule)]
    assert nodes
    assert "div" in serialize(nodes)


def test_roundtrip_simple() -> None:
    css = "a { color: blue }"
    out = serialize(parse_stylesheet(css))
    assert "color" in out and "blue" in out


def test_parse_at_rule() -> None:
    nodes = parse_stylesheet("@media screen { a { color: red } }")
    assert any(isinstance(n, AtRule) for n in nodes)
