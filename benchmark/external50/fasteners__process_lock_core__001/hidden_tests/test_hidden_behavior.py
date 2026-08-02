from __future__ import annotations

import re
from pathlib import Path

from featurelifted import InterProcessLock


def test_reacquire_after_release(tmp_path) -> None:
    lock_path = str(tmp_path / "reuse")
    lock = InterProcessLock(lock_path)
    assert lock.acquire() is True
    lock.release()
    assert lock.acquire() is True
    lock.release()


def test_nonblocking_acquire_free_lock(tmp_path) -> None:
    lock_path = str(tmp_path / "nb")
    lock = InterProcessLock(lock_path)
    assert lock.acquire(blocking=False) is True
    lock.release()


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\s*(?:from fasteners\b|import fasteners\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
