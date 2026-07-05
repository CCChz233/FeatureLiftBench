from __future__ import annotations

import re
from pathlib import Path

import pytest

from featurelifted import bucketize, chunked, get_path, unique


def test_chunked_fill_padding() -> None:
    assert chunked(range(10), 3, fill=None) == [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [9, None, None],
    ]


def test_chunked_count_limit() -> None:
    assert chunked(range(10), 3, count=2) == [[0, 1, 2], [3, 4, 5]]


def test_unique_key_preserves_first_of_length() -> None:
    words = ["hi", "hello", "ok", "bye", "yes"]
    assert unique(words, key=lambda x: len(x)) == ["hi", "hello", "bye"]


def test_bucketize_value_transform() -> None:
    src = ["aa", "bbb", "c"]
    out = bucketize(src, key=len, value_transform=lambda s: s.upper())
    assert out == {2: ["AA"], 3: ["BBB"], 1: ["C"]}


def test_partition_truthiness() -> None:
    from featurelifted import partition

    assert partition([0, 1, 2, 3]) == ([1, 2, 3], [0])


def test_get_path_missing_raises() -> None:
    root = {"users": [{"name": "ada"}]}
    assert get_path(root, ("users", 0, "name")) == "ada"
    with pytest.raises(KeyError):
        get_path(root, ("users", 9))


def test_no_boltons_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    import_pattern = re.compile(r"^\s*(?:from boltons|import boltons)\b", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert not import_pattern.search(text)
