from __future__ import annotations

import re
from pathlib import Path

from flask import Flask

from featurelifted import LoginManager, UserMixin, login_required, login_user


class User(UserMixin):
    def __init__(self, id_: str) -> None:
        self.id = id_


def test_login_required_redirects_anonymous() -> None:
    app = Flask(__name__)
    app.secret_key = "test"
    lm = LoginManager()
    lm.init_app(app)
    lm.login_view = "login"

    @lm.user_loader
    def load_user(user_id: str):
        return User(user_id)

    @app.route("/login")
    def login():
        return "login"

    @app.route("/private")
    @login_required
    def private():
        return "secret"

    client = app.test_client()
    resp = client.get("/private")
    assert resp.status_code in {302, 401}


def test_remember_flag() -> None:
    app = Flask(__name__)
    app.secret_key = "test"
    lm = LoginManager()
    lm.init_app(app)

    @lm.user_loader
    def load_user(user_id: str):
        return User(user_id)

    with app.test_request_context("/"):
        assert login_user(User("2"), remember=True) is True


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\s*(?:from flask_login\b|import flask_login\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
