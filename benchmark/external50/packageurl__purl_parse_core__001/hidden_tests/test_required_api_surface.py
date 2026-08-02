import featurelifted


def test_required_api_surface() -> None:
    assert hasattr(featurelifted, "PackageURL")
    assert callable(featurelifted.PackageURL.from_string)
    assert callable(featurelifted.PackageURL.to_string)
    assert callable(featurelifted.PackageURL.from_string)
    assert callable(featurelifted.PackageURL.to_string)
