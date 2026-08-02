from __future__ import annotations

import re
import time
from pathlib import Path

from featurelifted import (
    FileCreatedEvent,
    FileDeletedEvent,
    FileModifiedEvent,
    FileSystemEventHandler,
    Observer,
)


class Collect(FileSystemEventHandler):
    def __init__(self) -> None:
        self.events = []

    def on_any_event(self, event):  # type: ignore[override]
        self.events.append(type(event).__name__)


def test_modify_and_delete(tmp_path: Path) -> None:
    handler = Collect()
    obs = Observer(timeout=0.2)
    obs.schedule(handler, str(tmp_path), recursive=False)
    obs.start()
    try:
        f = tmp_path / "b.txt"
        f.write_text("1", encoding="utf-8")
        time.sleep(0.4)
        f.write_text("2", encoding="utf-8")
        time.sleep(0.4)
        f.unlink()
        deadline = time.time() + 3
        while time.time() < deadline and len(handler.events) < 2:
            time.sleep(0.1)
        assert handler.events
    finally:
        obs.stop()
        obs.join(timeout=3)


def test_event_types_exist() -> None:
    assert FileCreatedEvent is not None
    assert FileModifiedEvent is not None
    assert FileDeletedEvent is not None


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\s*(?:from watchdog\b|import watchdog\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
