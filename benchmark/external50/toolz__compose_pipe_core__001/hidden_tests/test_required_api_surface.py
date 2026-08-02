from featurelifted import compose, curry, identity, pipe


def test_required_api_surface() -> None:
    assert callable(compose) and callable(pipe) and callable(identity)
    assert curry is not None
