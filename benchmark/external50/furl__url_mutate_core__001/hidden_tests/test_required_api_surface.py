import featurelifted


def test_required_api_surface() -> None:
    assert hasattr(featurelifted, "Path")
    assert hasattr(featurelifted, "furl")
