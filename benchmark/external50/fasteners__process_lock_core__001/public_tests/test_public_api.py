from __future__ import annotations

from featurelifted import InterProcessLock


def test_acquire_release(tmp_path) -> None:
    lock_path = str(tmp_path / "lock")
    lock = InterProcessLock(lock_path)
    assert lock.acquire() is True
    lock.release()


def test_context_manager(tmp_path) -> None:
    lock_path = str(tmp_path / "lock2")
    with InterProcessLock(lock_path):
        pass
