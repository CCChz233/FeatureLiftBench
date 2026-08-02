from __future__ import annotations

from flask import Flask

from featurelifted import LoginManager, UserMixin, current_user, login_user, logout_user


class User(UserMixin):
    def __init__(self, id_: str) -> None:
        self.id = id_


def test_login_logout_current_user() -> None:
    app = Flask(__name__)
    app.secret_key = "test"
    lm = LoginManager()
    lm.init_app(app)

    @lm.user_loader
    def load_user(user_id: str):
        return User(user_id)

    with app.test_request_context("/"):
        user = User("1")
        assert login_user(user) is True
        user_proxy = current_user
        assert user_proxy.is_authenticated
        assert user_proxy.get_id() == "1"
        logout_user()
        user_proxy = current_user
        assert not user_proxy.is_authenticated


def test_user_mixin_anonymous() -> None:
    u = User("x")
    assert u.is_authenticated and not u.is_anonymous
