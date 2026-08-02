from featurelifted import fix_text


def test_required_api_surface() -> None:
    assert callable(fix_text)
