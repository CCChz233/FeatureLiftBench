from __future__ import annotations

import asyncio
from featurelifted import InMemoryBroker


def test_register_and_run_async_task() -> None:
    async def scenario() -> None:
        broker = InMemoryBroker(await_inplace=True)

        @broker.task
        async def add(left: int, right: int) -> int:
            return left + right

        assert await add(2, 3) == 5
        handle = await add.kiq(4, 7)
        assert await handle.is_ready()
        result = await handle.wait_result()
        assert result.return_value == 11

    asyncio.run(scenario())


def test_task_name_lookup() -> None:
    broker = InMemoryBroker()

    @broker.task(task_name="math.identity")
    async def identity(value: int) -> int:
        return value

    assert identity.task_name == "math.identity"
    assert broker.find_task("math.identity") is identity
