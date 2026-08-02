from featurelifted import ConfigUpdater


def test_required_api_surface() -> None:
    assert ConfigUpdater is not None
    cu = ConfigUpdater()
    assert hasattr(cu, "read_string") and hasattr(cu, "write")
