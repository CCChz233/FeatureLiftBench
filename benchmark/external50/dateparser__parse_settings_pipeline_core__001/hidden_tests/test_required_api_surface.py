from featurelifted import Settings, detect_languages, parse


def test_required_api_surface() -> None:
    assert callable(parse)
    assert callable(detect_languages)
    assert Settings is not None
