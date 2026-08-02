from featurelifted import chunked, consume, first, unique_everseen, windowed


def test_required_api_surface() -> None:
    assert all(callable(x) for x in (chunked, consume, first, unique_everseen, windowed))
