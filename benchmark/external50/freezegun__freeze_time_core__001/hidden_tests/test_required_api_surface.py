import featurelifted


def test_required_api_surface() -> None:
    assert hasattr(featurelifted, "FrozenDateTimeFactory")
    assert hasattr(featurelifted, "StepTickTimeFactory")
    assert hasattr(featurelifted, "TickingDateTimeFactory")
    assert hasattr(featurelifted, "freeze_time")
    assert callable(featurelifted.FrozenDateTimeFactory.tick)
    assert callable(featurelifted.FrozenDateTimeFactory.move_to)
    assert callable(featurelifted.TickingDateTimeFactory.tick)
    assert callable(featurelifted.TickingDateTimeFactory.move_to)
    assert callable(featurelifted.StepTickTimeFactory.tick)
    assert callable(featurelifted.StepTickTimeFactory.move_to)
