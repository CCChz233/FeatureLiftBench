from __future__ import annotations

import re
from pathlib import Path

from featurelifted import compose, curry, identity, pipe


def test_compose_right_to_left() -> None:
    order: list[str] = []

    def a(x: int) -> int:
        order.append("a")
        return x + 1

    def b(x: int) -> int:
        order.append("b")
        return x * 2

    assert compose(a, b)(3) == 7
    assert order == ["b", "a"]


def test_pipe_left_to_right() -> None:
    order: list[str] = []

    def a(x: int) -> int:
        order.append("a")
        return x + 1

    def b(x: int) -> int:
        order.append("b")
        return x * 2

    assert pipe(3, a, b) == 8
    assert order == ["a", "b"]


def test_curry_kwargs() -> None:
    def f(a: int, b: int, c: int = 0) -> int:
        return a + b + c

    cf = curry(f)
    assert cf(1)(2) == 3
    assert cf(1, c=4)(2) == 7


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\s*(?:from toolz\b|import toolz\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
