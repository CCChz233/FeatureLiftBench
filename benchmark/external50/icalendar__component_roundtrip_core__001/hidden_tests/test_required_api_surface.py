import featurelifted


def test_required_api_surface() -> None:
    assert hasattr(featurelifted, "Calendar")
    assert hasattr(featurelifted, "Event")
    assert callable(featurelifted.Calendar.from_ical)
    assert callable(featurelifted.Calendar.to_ical)
    assert callable(featurelifted.Calendar.add_component)
    assert callable(featurelifted.Calendar.from_ical)
    assert callable(featurelifted.Calendar.to_ical)
    assert callable(featurelifted.Event.add)
