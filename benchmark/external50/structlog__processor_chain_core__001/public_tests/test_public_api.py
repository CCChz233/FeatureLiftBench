from __future__ import annotations

import featurelifted as structlog


class ListLogger:
    def __init__(self):
        self.messages = []

    def msg(self, message):
        self.messages.append(message)

    def __getattr__(self, name):
        return self.msg


def test_bind_and_json_renderer() -> None:
    entries = []

    def factory(*args, **kwargs):
        logger = ListLogger()
        entries.append(logger)
        return logger

    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=factory,
        cache_logger_on_first_use=False,
    )
    log = structlog.get_logger().bind(user="a")
    log.info("hello", x=1)
    assert entries and '"user": "a"' in entries[0].messages[0]
    assert '"event": "hello"' in entries[0].messages[0]
    structlog.reset_defaults()


def test_key_value_renderer() -> None:
    sink = ListLogger()
    structlog.configure(
        processors=[structlog.processors.KeyValueRenderer()],
        logger_factory=lambda *a, **k: sink,
        cache_logger_on_first_use=False,
    )
    structlog.get_logger().info("evt", a=2)
    assert "a=2" in sink.messages[0] and "evt" in sink.messages[0]
    structlog.reset_defaults()
