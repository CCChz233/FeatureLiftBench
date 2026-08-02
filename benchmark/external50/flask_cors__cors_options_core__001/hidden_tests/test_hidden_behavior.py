from __future__ import annotations

import re
from pathlib import Path


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from flask_cors\\b|import flask_cors\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path


from flask import Flask

from featurelifted import CORS


def test_options_preflight() -> None:
    app = Flask(__name__)

    @app.route("/api", methods=["GET", "POST"])
    def api():
        return "data"

    CORS(app, methods=["GET", "POST"])
    client = app.test_client()
    resp = client.open(
        "/api",
        method="OPTIONS",
        headers={
            "Origin": "http://example.com",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert resp.status_code in {200, 204}
    assert "Access-Control-Allow-Methods" in resp.headers
