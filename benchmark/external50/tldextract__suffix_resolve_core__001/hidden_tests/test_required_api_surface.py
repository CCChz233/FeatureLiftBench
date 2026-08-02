import featurelifted


def test_required_api_surface() -> None:
    assert hasattr(featurelifted, "ExtractResult")
    assert hasattr(featurelifted, "TLDExtract")
    assert hasattr(featurelifted, "extract")
    assert callable(featurelifted.TLDExtract.__call__)
