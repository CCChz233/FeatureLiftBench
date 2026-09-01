from __future__ import annotations

from io import BytesIO

from featurelifted import App


def _environ(path: str, method: str = "GET") -> dict:
    return {
        "wsgi.version": (1, 0),
        "wsgi.url_scheme": "http",
        "wsgi.input": BytesIO(),
        "wsgi.errors": BytesIO(),
        "wsgi.multithread": False,
        "wsgi.multiprocess": False,
        "wsgi.run_once": False,
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "SCRIPT_NAME": "",
        "QUERY_STRING": "",
        "SERVER_NAME": "example.com",
        "SERVER_PORT": "80",
        "HTTP_HOST": "example.com",
        "CONTENT_LENGTH": "0",
    }


def _call(app: App, path: str, method: str = "GET") -> tuple[str, bytes]:
    captured: dict[str, str] = {}

    def start_response(status, headers, exc_info=None):
        captured["status"] = status

    body = b"".join(app(_environ(path, method), start_response))
    return captured["status"], body


class HelloResource:
    def on_get(self, req, resp):
        resp.status = "200 OK"
        resp.text = "hello"


class ItemResource:
    def on_get(self, req, resp, item_id):
        resp.status = "200 OK"
        resp.text = item_id


def test_registered_route_dispatches_get() -> None:
    app = App()
    app.add_route("/hello", HelloResource())
    status, body = _call(app, "/hello")
    assert status.startswith("200")
    assert b"hello" in body


def test_template_captures_path_parameter() -> None:
    app = App()
    app.add_route("/items/{item_id}", ItemResource())
    status, body = _call(app, "/items/42")
    assert status.startswith("200")
    assert b"42" in body


def test_unknown_path_is_not_found() -> None:
    app = App()
    app.add_route("/hello", HelloResource())
    status, _body = _call(app, "/missing")
    assert status.startswith("404")


def test_disallowed_method_is_not_allowed() -> None:
    app = App()
    app.add_route("/hello", HelloResource())
    status, _body = _call(app, "/hello", method="PUT")
    assert status.startswith("405")
