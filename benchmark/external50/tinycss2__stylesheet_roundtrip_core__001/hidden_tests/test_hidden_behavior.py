from __future__ import annotations

import re
from pathlib import Path

from featurelifted import parse_stylesheet, serialize
from featurelifted.ast import ParseError, QualifiedRule


def test_skip_whitespace_option() -> None:
    nodes = parse_stylesheet("div{}", skip_whitespace=True)
    assert all(not type(n).__name__.endswith("WhitespaceToken") for n in nodes)


def test_serialize_preserves_at_keyword() -> None:
    css = "@import url(x.css);"
    assert "@import" in serialize(parse_stylesheet(css))


def test_parse_error_node_not_raise() -> None:
    nodes = parse_stylesheet("}")
    assert any(isinstance(n, ParseError) for n in nodes)


def test_qualified_prelude() -> None:
    q = next(n for n in parse_stylesheet("h1.title{}") if isinstance(n, QualifiedRule))
    assert q.prelude


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\s*(?:from tinycss2\b|import tinycss2\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
