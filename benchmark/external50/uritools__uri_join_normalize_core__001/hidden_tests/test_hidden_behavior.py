from __future__ import annotations

import re
from pathlib import Path

from featurelifted import uriencode, uridecode, urijoin, urinorm, urisplit


def test_encode_decode_roundtrip() -> None:
    encoded = uriencode("你好")
    if isinstance(encoded, bytes):
        encoded_text = encoded.decode("ascii")
    else:
        encoded_text = encoded
    assert "%" in encoded_text
    assert uridecode(encoded) == "你好"


def test_urijoin_strict_absolute_ref() -> None:
    assert urijoin("https://example.com/a", "https://other.test/x", strict=True) == "https://other.test/x"


def test_urinorm_scheme_case() -> None:
    out = urinorm("HTTP://Example.COM/a/./b")
    assert out.startswith("http://")
    assert "/a/b" in out or out.endswith("/a/b")


def test_split_relative_ref() -> None:
    parts = urisplit("/rel/path")
    assert parts.scheme is None or parts.scheme == ""
    assert parts.path == "/rel/path"


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\s*(?:from uritools|import uritools)\b", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8"))
