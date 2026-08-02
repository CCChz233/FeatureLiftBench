from __future__ import annotations

from featurelifted import BooleanAlgebra


def test_parse_and_simplify() -> None:
    algebra = BooleanAlgebra()
    expr = algebra.parse("a & b | ~c")
    simplified = expr.simplify()
    assert simplified == algebra.parse("~c | (a & b)") or str(simplified) == "~c|(a&b)"


def test_subs() -> None:
    algebra = BooleanAlgebra()
    a_sym = algebra.Symbol("a")
    expr = algebra.parse("a & b | ~c")
    subbed = expr.subs({a_sym: algebra.TRUE}, simplify=True)
    assert subbed == algebra.parse("b | ~c") or str(subbed) == "b|~c"


def test_equality() -> None:
    algebra = BooleanAlgebra()
    left = algebra.parse("a | b")
    right = algebra.parse("b | a")
    assert left.simplify() == right.simplify()
