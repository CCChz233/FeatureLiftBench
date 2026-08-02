import featurelifted


def test_required_api_surface() -> None:
    assert hasattr(featurelifted, "BaseCache")
    assert hasattr(featurelifted, "CacheController")
    assert hasattr(featurelifted, "DictCache")
    assert hasattr(featurelifted, "ExpiresAfter")
    assert hasattr(featurelifted, "Serializer")
    assert callable(featurelifted.DictCache.get)
    assert callable(featurelifted.DictCache.set)
    assert callable(featurelifted.DictCache.delete)
