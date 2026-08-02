from featurelifted import URL, URLParseError


def test_required_api_surface() -> None:
    assert URL is not None and URLParseError is not None
    assert hasattr(URL, "from_text")
    url = URL.from_text("https://example.com")
    assert callable(url.to_text) and callable(url.replace) and callable(url.click)
