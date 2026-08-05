from __future__ import annotations

import re
from pathlib import Path

import pytest

from featurelifted import decode, encode
from featurelifted.exceptions import InvalidSignatureError, InvalidTokenError


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\s*(?:from jwt\b|import jwt\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path


def test_custom_header() -> None:
    token = encode({"x": 1}, "k", algorithm="HS256", headers={"kid": "1"})
    payload = decode(token, "k", algorithms=["HS256"])
    assert payload["x"] == 1


def test_invalid_token_error_base() -> None:
    assert issubclass(InvalidTokenError, Exception)


def test_wrong_secret_hidden() -> None:
    token = encode({"scope": "hidden"}, "right", algorithm="HS256")
    with pytest.raises(InvalidSignatureError):
        decode(token, "wrong", algorithms=["HS256"])
