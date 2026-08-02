import featurelifted


def test_required_api_surface() -> None:
    assert hasattr(featurelifted, "LoginManager")
    assert hasattr(featurelifted, "UserMixin")
    assert hasattr(featurelifted, "current_user")
    assert hasattr(featurelifted, "login_required")
    assert hasattr(featurelifted, "login_user")
    assert hasattr(featurelifted, "logout_user")
    assert callable(featurelifted.LoginManager.init_app)
    assert callable(featurelifted.LoginManager.user_loader)
