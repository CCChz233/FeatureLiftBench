from __future__ import annotations

from featurelifted import furl


def test_parse_and_mutate_path() -> None:
    u = furl("https://example.com/a/b")
    u.path.segments.append("c")
    assert "/a/b/c" in u.url


def test_query_args() -> None:
    u = furl("https://example.com/?a=1")
    u.args["b"] = "2"
    assert "a=1" in u.url and "b=2" in u.url


def test_set_scheme_host() -> None:
    u = furl("http://old.test/x")
    u.scheme = "https"
    u.host = "new.test"
    assert u.url.startswith("https://new.test/")
