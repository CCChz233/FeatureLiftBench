from __future__ import annotations

from featurelifted import MemoryHuey


def _run_one(huey: MemoryHuey) -> None:
    task = huey.dequeue()
    assert task is not None
    huey.execute(task)


def test_multiple_tasks() -> None:
    huey = MemoryHuey(utc=False)
    @huey.task()
    def mul(a: int, b: int) -> int:
        return a * b

    r1 = mul(2, 3)
    r2 = mul(4, 5)
    _run_one(huey)
    _run_one(huey)
    assert r1.get(blocking=False) == 6
    assert r2.get(blocking=False) == 20


def test_flush_clears_queue() -> None:
    huey = MemoryHuey(utc=False)
    @huey.task()
    def noop() -> int:
        return 0

    noop()
    assert huey.pending_count() >= 1
    huey.flush()
    assert huey.pending_count() == 0


def test_no_upstream_import_surface() -> None:
    import re
    from pathlib import Path
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(
        rf"^\s*(?:from huey\b|import huey\b)",
        re.MULTILINE,
    )
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
