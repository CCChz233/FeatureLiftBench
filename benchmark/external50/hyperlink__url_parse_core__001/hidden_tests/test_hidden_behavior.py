from __future__ import annotations

import re
from pathlib import Path


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from hyperlink\\b|import hyperlink\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path


from featurelifted import URL, URLParseError


def test_immutable_replace() -> None:
    original = URL.from_text("https://example.com/x")
    changed = original.replace(path=["y"])
    assert original.to_text().endswith("/x")
    assert changed.to_text().endswith("/y")


def test_parse_error() -> None:
    try:
        URL.from_text("http://[::1/")
        assert False, "expected URLParseError"
    except URLParseError:
        pass
