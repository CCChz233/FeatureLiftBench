import featurelifted


def test_required_api_surface() -> None:
    assert hasattr(featurelifted, "MemoryHuey")
    assert hasattr(featurelifted, "crontab")
    assert callable(featurelifted.MemoryHuey.task)
    assert callable(featurelifted.MemoryHuey.pending_count)
    assert callable(featurelifted.MemoryHuey.flush)
