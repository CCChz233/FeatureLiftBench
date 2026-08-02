import featurelifted


def test_required_api_surface() -> None:
    assert hasattr(featurelifted, "JSONStorage")
    assert hasattr(featurelifted, "MemoryStorage")
    assert hasattr(featurelifted, "Query")
    assert hasattr(featurelifted, "TinyDB")
    instance_0 = featurelifted.TinyDB(storage=featurelifted.MemoryStorage)
    assert callable(instance_0.insert)
    assert callable(instance_0.insert_multiple)
    assert callable(instance_0.all)
    assert callable(instance_0.get)
    assert callable(instance_0.search)
    assert callable(instance_0.update)
    assert callable(instance_0.remove)
    assert callable(instance_0.truncate)
    assert callable(instance_0.close)
    assert callable(featurelifted.Query.__getattr__)
    assert callable(featurelifted.Query.__getitem__)
    assert callable(featurelifted.Query.exists)
    assert callable(featurelifted.Query.matches)
    assert callable(featurelifted.Query.test)
    instance_0.close()
