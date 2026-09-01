from __future__ import annotations

import urllib.request
from contextlib import contextmanager

from featurelifted import GET, disable, enable, last_request, register_uri, reset


@contextmanager
def stubbed():
    enable(allow_net_connect=False)
    try:
        yield
    finally:
        disable()
        reset()


def test_get_stub_body() -> None:
    with stubbed():
        register_uri(GET, "http://example.test/hello", body="world")
        with urllib.request.urlopen("http://example.test/hello") as response:
            assert response.read() == b"world"
            assert response.status == 200


def test_last_request_path() -> None:
    with stubbed():
        register_uri(GET, "http://example.test/hello", body="ok")
        urllib.request.urlopen("http://example.test/hello").read()
        assert last_request().path == "/hello"


def test_querystring_recorded() -> None:
    with stubbed():
        register_uri(GET, "http://example.test/search?q=flb", body="hit")
        urllib.request.urlopen("http://example.test/search?q=flb").read()
        assert last_request().querystring == {"q": ["flb"]}
