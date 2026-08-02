import featurelifted


def test_required_api_surface() -> None:
    assert hasattr(featurelifted, "FileCreatedEvent")
    assert hasattr(featurelifted, "FileDeletedEvent")
    assert hasattr(featurelifted, "FileModifiedEvent")
    assert hasattr(featurelifted, "FileSystemEventHandler")
    assert hasattr(featurelifted, "Observer")
    assert callable(featurelifted.Observer.schedule)
    assert callable(featurelifted.Observer.start)
    assert callable(featurelifted.Observer.stop)
    assert callable(featurelifted.Observer.join)
