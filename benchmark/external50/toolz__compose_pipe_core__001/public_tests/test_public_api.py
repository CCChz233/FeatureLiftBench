from __future__ import annotations

from featurelifted import compose, curry, identity, pipe


def test_compose_and_pipe() -> None:
    f = compose(lambda x: x + 1, lambda x: x * 2)
    assert f(3) == 7
    assert pipe(3, lambda x: x * 2, lambda x: x + 1) == 7


def test_curry_partial() -> None:
    add = curry(lambda a, b: a + b)
    assert add(1)(2) == 3
    assert add(1, 2) == 3


def test_identity() -> None:
    assert identity(42) == 42
    assert compose(identity, identity)(5) == 5
