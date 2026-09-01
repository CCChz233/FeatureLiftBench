from __future__ import annotations

import pytest
from featurelifted import create_task_group, fail_after, run, sleep


def test_task_group_runs_spawned_coroutines() -> None:
    async def main():
        seen: list[int] = []

        async def add(value: int) -> None:
            seen.append(value)

        async with create_task_group() as tg:
            tg.create_task(add(1))
            tg.create_task(add(2))
        return sorted(seen)

    assert run(main) == [1, 2]


def test_fail_after_timeout() -> None:
    async def main() -> None:
        with fail_after(0.05):
            await sleep(1)

    with pytest.raises(TimeoutError):
        run(main)
