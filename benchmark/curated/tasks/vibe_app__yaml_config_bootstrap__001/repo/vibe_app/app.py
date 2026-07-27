"""Application factory with lazy imports and global bootstrap."""

from __future__ import annotations

from vibe_app.routes import FakeApp, register_routes
from vibe_app.state import GLOBAL_STATE


def create_app(config_dir: str = "config") -> FakeApp:
    if not GLOBAL_STATE.get("bootstrapped"):
        from vibe_app.config_loader import bootstrap_config

        bootstrap_config(config_dir)
    app = FakeApp("vibeshop")
    register_routes(app)
    return app
