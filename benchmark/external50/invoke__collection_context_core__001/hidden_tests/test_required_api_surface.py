import featurelifted


def test_required_api_surface() -> None:
    assert hasattr(featurelifted, "Collection")
    assert hasattr(featurelifted, "Context")
    assert hasattr(featurelifted, "MockContext")
    assert hasattr(featurelifted, "UnexpectedExit")
    assert hasattr(featurelifted, "task")
    assert callable(featurelifted.Collection.add_task)
    assert callable(featurelifted.Collection.add_collection)
    assert callable(featurelifted.MockContext.run)
