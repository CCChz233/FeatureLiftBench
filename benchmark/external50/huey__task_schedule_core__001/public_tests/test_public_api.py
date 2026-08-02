from __future__ import annotations

from datetime import datetime

from featurelifted import MemoryHuey, crontab


def _run_task(huey: MemoryHuey, result) -> None:
    task = huey.dequeue()
    assert task is not None
    huey.execute(task)


def test_task_enqueue_and_result() -> None:
    huey = MemoryHuey(utc=False)
    @huey.task()
    def add(a: int, b: int) -> int:
        return a + b

    result = add(1, 2)
    _run_task(huey, result)
    assert result.get(blocking=False) == 3


def test_crontab_helper() -> None:
    schedule = crontab(minute="*/5")
    assert callable(schedule)
    when = datetime(2024, 1, 1, 10, 5, 0)
    assert schedule(when) is True
    assert schedule(datetime(2024, 1, 1, 10, 3, 0)) is False
