from __future__ import annotations

import json
import logging

from featurelifted import JsonFormatter


def test_basic_json_line() -> None:
    fmt = JsonFormatter("%(message)s %(levelname)s")
    record = logging.LogRecord("app", logging.INFO, __file__, 10, "hello", (), None)
    payload = json.loads(fmt.format(record))
    assert payload["message"] == "hello"
    assert payload["levelname"] == "INFO"


def test_rename_and_static_fields() -> None:
    fmt = JsonFormatter(
        "%(message)s %(levelname)s",
        rename_fields={"levelname": "level"},
        static_fields={"app": "svc"},
    )
    record = logging.LogRecord("app", logging.WARNING, __file__, 1, "warn", (), None)
    payload = json.loads(fmt.format(record))
    assert payload["level"] == "WARNING"
    assert payload["app"] == "svc"
    assert "levelname" not in payload
