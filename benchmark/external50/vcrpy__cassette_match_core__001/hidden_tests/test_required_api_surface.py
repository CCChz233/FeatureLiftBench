import featurelifted


def test_required_api_surface() -> None:
    assert hasattr(featurelifted, "Cassette")
    assert hasattr(featurelifted, "VCR")
    assert hasattr(featurelifted, "use_cassette")
    assert callable(featurelifted.VCR.use_cassette)
    assert callable(featurelifted.VCR.use_cassette)
