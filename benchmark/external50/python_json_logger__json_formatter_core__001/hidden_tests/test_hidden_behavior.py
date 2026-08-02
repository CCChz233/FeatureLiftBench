from __future__ import annotations

import json
import logging

from featurelifted import JsonFormatter


def test_custom_fmt_fields() -> None:
    fmt = JsonFormatter("%(message)s %(name)s")
    record = logging.LogRecord("worker", logging.ERROR, __file__, 3, "boom", (), None)
    payload = json.loads(fmt.format(record))
    assert payload["message"] == "boom"
    assert payload["name"] == "worker"


def test_no_upstream_import_surface() -> None:
    import re
    from pathlib import Path
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(
        rf"^\s*(?:from pythonjsonlogger\b|import pythonjsonlogger\b)",
        re.MULTILINE,
    )
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
