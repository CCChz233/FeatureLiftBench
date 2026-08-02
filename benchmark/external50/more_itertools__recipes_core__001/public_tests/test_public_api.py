from __future__ import annotations

from featurelifted import chunked, consume, first, unique_everseen, windowed


def test_chunked_and_first() -> None:
    assert list(chunked(range(5), 2)) == [[0, 1], [2, 3], [4]]
    assert first(x for x in [0, 1, 2]) == 0


def test_unique_everseen() -> None:
    assert list(unique_everseen([1, 2, 1, 3, 2])) == [1, 2, 3]


def test_consume_and_windowed() -> None:
    it = iter(range(5))
    consume(it, 2)
    assert next(it) == 2
    assert list(windowed([1, 2, 3, 4], 3)) == [(1, 2, 3), (2, 3, 4)]
