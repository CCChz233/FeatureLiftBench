import featurelifted as structlog


def test_required_api_surface() -> None:
    assert callable(structlog.configure)
    assert callable(structlog.get_logger)
    assert callable(structlog.reset_defaults)
    assert structlog.processors.JSONRenderer is not None
    assert structlog.processors.KeyValueRenderer is not None
    assert structlog.processors.TimeStamper is not None
    assert structlog.processors.add_log_level is not None
