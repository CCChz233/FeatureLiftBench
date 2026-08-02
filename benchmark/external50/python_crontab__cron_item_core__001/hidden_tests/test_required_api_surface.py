import featurelifted


def test_required_api_surface() -> None:
    assert hasattr(featurelifted, "CronItem")
    assert hasattr(featurelifted, "CronSlices")
    assert callable(featurelifted.CronSlices.is_valid)
    assert callable(featurelifted.CronSlices.setall)
    assert callable(featurelifted.CronSlices.render)
    assert callable(featurelifted.CronSlices.is_valid)
    assert callable(featurelifted.CronItem.render)
    assert callable(featurelifted.CronItem.is_valid)
    assert callable(featurelifted.CronItem.is_enabled)
    assert callable(featurelifted.CronItem.render)
    assert callable(featurelifted.CronItem.is_valid)
