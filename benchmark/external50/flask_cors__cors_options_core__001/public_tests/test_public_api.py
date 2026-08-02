from __future__ import annotations

from flask import Flask

from featurelifted import CORS, cross_origin


def test_cors_app_headers() -> None:
    app = Flask(__name__)

    @app.route("/")
    def index():
        return "ok"

    CORS(app)
    client = app.test_client()
    resp = client.get("/", headers={"Origin": "http://example.com"})
    assert resp.status_code == 200
    assert resp.headers.get("Access-Control-Allow-Origin") in (
        "http://example.com",
        "*",
    )


def test_cross_origin_decorator() -> None:
    app = Flask(__name__)

    @app.route("/x")
    @cross_origin(origins="https://a.test")
    def x():
        return "x"

    client = app.test_client()
    resp = client.get("/x", headers={"Origin": "https://a.test"})
    assert resp.headers.get("Access-Control-Allow-Origin") == "https://a.test"
