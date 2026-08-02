from __future__ import annotations

from featurelifted import urijoin, urinorm, urisplit, uriunsplit


def test_urisplit_fields() -> None:
    parts = urisplit("https://example.com/a/b?q=1#frag")
    assert parts.scheme == "https"
    assert parts.authority == "example.com"
    assert parts.path == "/a/b"
    assert parts.query == "q=1"
    assert parts.fragment == "frag"
    assert uriunsplit(parts) == "https://example.com/a/b?q=1#frag"


def test_urijoin_relative() -> None:
    assert urijoin("https://example.com/a/", "../b") == "https://example.com/b"


def test_urinorm_path_dots() -> None:
    assert urinorm("https://example.com/a/./b/../c") == "https://example.com/a/c"
