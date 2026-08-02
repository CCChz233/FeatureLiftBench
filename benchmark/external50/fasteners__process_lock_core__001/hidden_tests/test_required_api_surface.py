from featurelifted import InterProcessLock


def test_required_api_surface() -> None:
    assert InterProcessLock is not None
