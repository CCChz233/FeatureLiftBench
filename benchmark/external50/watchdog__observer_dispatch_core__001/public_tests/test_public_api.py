from __future__ import annotations

import time
from pathlib import Path

from featurelifted import FileSystemEventHandler, Observer


class Handler(FileSystemEventHandler):
    def __init__(self) -> None:
        self.created = []

    def on_created(self, event):  # type: ignore[override]
        self.created.append(event.src_path)


def test_observer_create_event(tmp_path: Path) -> None:
    handler = Handler()
    obs = Observer(timeout=0.2)
    obs.schedule(handler, str(tmp_path), recursive=False)
    obs.start()
    try:
        target = tmp_path / "a.txt"
        target.write_text("x", encoding="utf-8")
        deadline = time.time() + 3
        while time.time() < deadline and not handler.created:
            time.sleep(0.1)
        assert any(str(target) in p or p.endswith("a.txt") for p in handler.created)
    finally:
        obs.stop()
        obs.join(timeout=3)
