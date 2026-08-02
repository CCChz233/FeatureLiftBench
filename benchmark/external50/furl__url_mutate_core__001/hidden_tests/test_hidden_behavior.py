from __future__ import annotations

import re
from pathlib import Path


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from furl\\b|import furl\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path


from featurelifted import furl


def test_fragment_and_port() -> None:
    u = furl("https://example.com:8080/path#frag")
    u.port = 9090
    u.fragment = "updated"
    assert ":9090/" in u.url
    assert "#updated" in u.url


def test_remove_query_key() -> None:
    u = furl("https://x.test/?a=1&b=2")
    del u.args["a"]
    assert "a=" not in u.url
    assert "b=2" in u.url
