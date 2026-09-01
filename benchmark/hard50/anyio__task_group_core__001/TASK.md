# FeatureLift Task: TaskGroup create_task and cancel

Build a standalone `featurelifted` package providing AnyIO-style task groups, cancellation, and timeout scopes driven by `run`, without network IO.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    create_task_group,
    fail_after,
    get_cancelled_exc_class,
    run,
    sleep,
)
```

## Required API Details

- `create_task_group() -> TaskGroup`
- `run(func, *args) -> Any`
- `fail_after(delay: float)`
- `sleep(delay: float) -> None`
- `get_cancelled_exc_class() -> type[BaseException]`

## Required Behavior

- `run` executes an async entrypoint. Tasks started with `TaskGroup.create_task(coro)` inside `async with create_task_group()` all complete before the context exits, and their side effects are visible afterwards.
- Calling `cancel()` on an open task group cancels pending tasks so they observe the exception class returned by `get_cancelled_exc_class()`.
- A `fail_after(seconds)` block whose body awaits `sleep` longer than that deadline raises `TimeoutError` when driven by `run`.
- Task-group execution does not perform network name resolution or open sockets; cancellation and timeouts are local to the running event loop.
- The package exposes `create_task_group`, `run`, `fail_after`, `sleep`, and `get_cancelled_exc_class` as listed in this contract.
- The submitted package source does not import the forbidden upstream package `anyio`.

## Constraints

- Forbidden imports: `anyio`.
- Do not implement trio plus asyncio production servers.
- Do not implement real TCP/UNIX network clients.
- Do not implement runtime import of anyio.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — `run` executes an async entrypoint. Tasks started with `TaskGroup.create_task(coro)` inside `async with create_task_group()` all complete before the context exits, and their side effects are visible afterwards.
- **B002** — Calling `cancel()` on an open task group cancels pending tasks so they observe the exception class returned by `get_cancelled_exc_class()`.
- **B003** — A `fail_after(seconds)` block whose body awaits `sleep` longer than that deadline raises `TimeoutError` when driven by `run`.
- **B004** — Task-group execution does not perform network name resolution or open sockets; cancellation and timeouts are local to the running event loop.
- **B005** — The package exposes `create_task_group`, `run`, `fail_after`, `sleep`, and `get_cancelled_exc_class` as listed in this contract.
- **B006** — The submitted package source does not import the forbidden upstream package `anyio`.
<!-- featureliftbench:behavior-clauses:end -->
