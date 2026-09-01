from __future__ import annotations

from featurelifted import URLMap


def _app(tag: str):
    def application(environ, start_response):
        start_response("200 OK", [("Content-Type", "text/plain")])
        return [tag.encode("ascii") + environ["PATH_INFO"].encode("ascii")]

    return application


def _call(mapper, path: str, host: str = "localhost"):
    captured: dict[str, str] = {}

    def start_response(status, headers, exc_info=None):
        captured["status"] = status

    environ = {
        "PATH_INFO": path,
        "SCRIPT_NAME": "",
        "HTTP_HOST": host,
        "SERVER_NAME": host,
        "wsgi.url_scheme": "http",
        "REQUEST_METHOD": "GET",
    }
    body = b"".join(mapper(environ, start_response))
    return captured["status"], body, environ["SCRIPT_NAME"], environ["PATH_INFO"]


def test_prefix_dispatch_strips_matched_path() -> None:
    mapper = URLMap()
    mapper["/foo"] = _app("FOO")
    status, body, script, rest = _call(mapper, "/foo")
    assert status.startswith("200")
    assert body == b"FOO"
    assert script == "/foo"
    assert rest == ""


def test_longest_prefix_wins() -> None:
    mapper = URLMap()
    mapper["/foo"] = _app("FOO")
    mapper["/foo/bar"] = _app("BAR")
    status, body, script, rest = _call(mapper, "/foo/bar")
    assert status.startswith("200")
    assert body == b"BAR"
    assert script == "/foo/bar"
    assert rest == ""


def test_unknown_path_is_not_found() -> None:
    mapper = URLMap()
    mapper["/foo"] = _app("FOO")
    status, body, _, _ = _call(mapper, "/missing")
    assert status.startswith("404")
    assert b"404" in body


def test_remaining_path_is_forwarded() -> None:
    mapper = URLMap()
    mapper["/foo"] = _app("FOO")
    status, body, script, rest = _call(mapper, "/foo/x")
    assert status.startswith("200")
    assert body == b"FOO/x"
    assert script == "/foo"
    assert rest == "/x"
