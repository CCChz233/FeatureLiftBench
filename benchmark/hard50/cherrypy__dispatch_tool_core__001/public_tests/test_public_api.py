from __future__ import annotations

import io
import sys

from featurelifted import Application, expose


class Root:
    @expose
    def index(self):
        return "idx"

    @expose
    def hello(self):
        return "hello"


def _call(app, path: str) -> tuple[str, bytes]:
    captured: dict[str, str] = {}

    def start_response(status, headers, exc_info=None):
        captured["status"] = status

    environ = {
        "PATH_INFO": path,
        "SCRIPT_NAME": "",
        "REQUEST_METHOD": "GET",
        "SERVER_NAME": "localhost",
        "SERVER_PORT": "80",
        "SERVER_PROTOCOL": "HTTP/1.1",
        "HTTP_HOST": "localhost",
        "wsgi.version": (1, 0),
        "wsgi.url_scheme": "http",
        "wsgi.input": io.BytesIO(),
        "wsgi.errors": sys.stderr,
        "wsgi.multithread": False,
        "wsgi.multiprocess": False,
        "wsgi.run_once": True,
        "QUERY_STRING": "",
        "CONTENT_LENGTH": "0",
    }
    body = b"".join(app(environ, start_response))
    return captured["status"], body


def test_index_dispatch() -> None:
    status, body = _call(Application(Root()), "/")
    assert status.startswith("200")
    assert b"idx" in body


def test_named_handler_dispatch() -> None:
    status, body = _call(Application(Root()), "/hello")
    assert status.startswith("200")
    assert b"hello" in body


def test_unknown_path_is_not_found() -> None:
    status, body = _call(Application(Root()), "/missing")
    assert status.startswith("404")
    assert b"404" in body or b"Not Found" in body


def test_expose_marks_handler() -> None:
    assert Root.hello.exposed is True
    assert Root.index.exposed is True
