"""Flask-ish routes — framework coupling clutter."""

from __future__ import annotations

from vibe_app.config_loader import bootstrap_config
from vibe_app.csv_transform.pipeline import TransformOptions, transform_csv
from vibe_app.services.order_service import order_line_total
from vibe_app.utils import calc_price_legacy, calc_price_v1, compute_line_price


class FakeRequest:
    def __init__(self, json: dict | None = None):
        self.json = json or {}


class FakeApp:
    def __init__(self, name: str):
        self.name = name
        self._routes: dict[str, object] = {}

    def route(self, path: str):
        def decorator(func):
            self._routes[path] = func
            return func

        return decorator


def register_routes(app: FakeApp) -> None:
    @app.route("/health")
    def health():
        return {"ok": True}

    @app.route("/price")
    def price(request: FakeRequest | None = None):
        payload = (request or FakeRequest()).json
        # legacy path still wired for old clients
        if payload.get("legacy"):
            return {"total": calc_price_legacy(payload["unit_price"], payload["quantity"], payload["category"])}
        if payload.get("v1"):
            return {"total": calc_price_v1(payload["unit_price"], payload["quantity"], payload["category"])}
        return {
            "total": compute_line_price(
                payload["unit_price"],
                payload["quantity"],
                payload["category"],
            )
        }

    @app.route("/csv")
    def csv_route(request: FakeRequest | None = None):
        payload = (request or FakeRequest()).json
        opts = TransformOptions(min_quantity=int(payload.get("min_quantity", 0)))
        return {"rows": transform_csv(payload["csv"], options=opts)}

    @app.route("/bootstrap")
    def bootstrap_route(request: FakeRequest | None = None):
        payload = (request or FakeRequest()).json
        return bootstrap_config(payload.get("config_dir", "config"))
