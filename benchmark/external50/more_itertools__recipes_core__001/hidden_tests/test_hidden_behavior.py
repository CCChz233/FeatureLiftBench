from __future__ import annotations

import re
from pathlib import Path

from featurelifted import chunked, consume, first, unique_everseen, windowed


def test_chunked_strict() -> None:
    try:
        list(chunked([1, 2, 3], 2, strict=True))
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_unique_everseen_key() -> None:
    data = ["A", "a", "B", "b"]
    assert list(unique_everseen(data, key=str.lower)) == ["A", "B"]


def test_windowed_fillvalue() -> None:
    assert list(windowed([1, 2], 3, fillvalue=0)) == [(1, 2, 0)]


def test_consume_all() -> None:
    it = iter(range(3))
    consume(it)
    assert list(it) == []


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\s*(?:from more_itertools\b|import more_itertools\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
