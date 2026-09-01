from __future__ import annotations

from featurelifted import parse


def test_parse_https_example() -> None:
    scheme, host, port, path = parse("https://example.com/foo")
    assert scheme == b"https"
    assert host == b"example.com"
    assert port == 443
    assert path == b"/foo"


def test_parse_http_ipv4_port() -> None:
    scheme, host, port, path = parse("http://127.0.0.1:8080/x")
    assert scheme == b"http"
    assert host == b"127.0.0.1"
    assert port == 8080
    assert path == b"/x"
