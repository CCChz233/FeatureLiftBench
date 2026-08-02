from __future__ import annotations

from featurelifted import LOCK_EX, Lock, lock, unlock


def test_lock_context_manager(tmp_path) -> None:
    path = tmp_path / "data.txt"
    path.write_text("x", encoding="utf-8")
    with Lock(str(path), mode="a") as fh:
        fh.write("y")
    assert "xy" in path.read_text(encoding="utf-8")


def test_lock_unlock_functions(tmp_path) -> None:
    path = tmp_path / "raw.txt"
    path.write_text("a", encoding="utf-8")
    fh = open(path, "a")
    try:
        lock(fh, LOCK_EX)
        fh.write("b")
        unlock(fh)
    finally:
        fh.close()
    assert path.read_text(encoding="utf-8") == "ab"
