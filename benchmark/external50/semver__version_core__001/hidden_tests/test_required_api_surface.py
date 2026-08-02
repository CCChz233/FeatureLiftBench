import featurelifted


def test_required_api_surface() -> None:
    assert hasattr(featurelifted, "Version")
    assert callable(featurelifted.Version.parse)
    assert callable(featurelifted.Version.compare)
    assert callable(featurelifted.Version.bump_major)
    assert callable(featurelifted.Version.bump_minor)
    assert callable(featurelifted.Version.bump_patch)
    assert callable(featurelifted.Version.replace)
