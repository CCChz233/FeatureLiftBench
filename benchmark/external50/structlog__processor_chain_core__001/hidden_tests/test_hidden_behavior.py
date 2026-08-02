from __future__ import annotations

import re
from pathlib import Path

import featurelifted as structlog


class ListLogger:
    def __init__(self):
        self.messages = []

    def msg(self, message):
        self.messages.append(message)

    def __getattr__(self, name):
        return self.msg


def test_timestamp_and_unbind() -> None:
    sink = ListLogger()
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=lambda *a, **k: sink,
        cache_logger_on_first_use=False,
    )
    log = structlog.get_logger().bind(k=1).unbind("k").bind(k=2)
    log.warning("w")
    msg = sink.messages[0]
    assert '"k": 2' in msg and "timestamp" in msg and '"level": "warning"' in msg
    structlog.reset_defaults()


def test_new_context() -> None:
    sink = ListLogger()
    structlog.configure(
        processors=[structlog.processors.JSONRenderer()],
        logger_factory=lambda *a, **k: sink,
        cache_logger_on_first_use=False,
    )
    log = structlog.get_logger().bind(a=1).new(b=2)
    log.info("n")
    assert '"b": 2' in sink.messages[0] and '"a"' not in sink.messages[0]
    structlog.reset_defaults()


def test_processor_order() -> None:
    seen = []

    def mark(name):
        def proc(logger, method_name, event_dict):
            seen.append(name)
            return event_dict

        return proc

    sink = ListLogger()
    structlog.configure(
        processors=[mark("a"), mark("b"), structlog.processors.JSONRenderer()],
        logger_factory=lambda *a, **k: sink,
        cache_logger_on_first_use=False,
    )
    structlog.get_logger().info("x")
    assert seen == ["a", "b"]
    structlog.reset_defaults()


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\s*(?:from structlog\b|import structlog\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
