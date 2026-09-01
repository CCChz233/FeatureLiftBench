from __future__ import annotations

import asyncio

from featurelifted import Blueprint, Quart


def _run(coro):
    return asyncio.run(coro)


def test_app_route_dispatch() -> None:
    app = Quart(__name__)

    @app.route("/hi")
    async def hi():
        return "hello"

    async def body():
        client = app.test_client()
        response = await client.get("/hi")
        return response.status_code, await response.get_data(as_text=True)

    status, text = _run(body())
    assert status == 200
    assert text == "hello"


def test_blueprint_prefix_dispatch() -> None:
    app = Quart(__name__)
    blueprint = Blueprint("api", __name__)

    @blueprint.route("/item")
    async def item():
        return "item"

    app.register_blueprint(blueprint, url_prefix="/api")

    async def body():
        client = app.test_client()
        response = await client.get("/api/item")
        return response.status_code, await response.get_data(as_text=True)

    status, text = _run(body())
    assert status == 200
    assert text == "item"


def test_unknown_path_is_not_found() -> None:
    app = Quart(__name__)

    @app.route("/only")
    async def only():
        return "only"

    async def body():
        client = app.test_client()
        response = await client.get("/missing")
        return response.status_code

    assert _run(body()) == 404


def test_root_route() -> None:
    app = Quart(__name__)

    @app.route("/")
    async def index():
        return "root"

    async def body():
        client = app.test_client()
        response = await client.get("/")
        return response.status_code, await response.get_data(as_text=True)

    status, text = _run(body())
    assert status == 200
    assert text == "root"
