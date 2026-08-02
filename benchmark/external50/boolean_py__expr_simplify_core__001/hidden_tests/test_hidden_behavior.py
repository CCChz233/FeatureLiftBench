from __future__ import annotations

from featurelifted import BooleanAlgebra, ParseError


def test_parse_error() -> None:
    algebra = BooleanAlgebra()
    try:
        algebra.parse("a &")
        assert False, "expected ParseError"
    except ParseError:
        pass


def test_not_and_constants() -> None:
    algebra = BooleanAlgebra()
    expr = algebra.parse("~TRUE")
    assert expr.simplify() == algebra.FALSE


def test_symbol_roundtrip() -> None:
    algebra = BooleanAlgebra()
    sym = algebra.Symbol("x")
    expr = algebra.parse("x")
    assert expr.subs({sym: algebra.TRUE}) == algebra.TRUE


def test_no_upstream_import_surface() -> None:
    import re
    from pathlib import Path
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(
        rf"^\s*(?:from boolean\b|import boolean\b)",
        re.MULTILINE,
    )
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
