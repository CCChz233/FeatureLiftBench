from featurelifted import CORS, cross_origin


def test_required_api_surface() -> None:
    assert CORS is not None and callable(cross_origin)
