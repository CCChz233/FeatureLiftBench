# FeatureLift Task: In-memory broker task execution

Extract a standalone in-memory task broker with task registration, `kiq` dispatch, and result retrieval into `featurelifted`.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    DecoratedTask,
    InMemoryBroker,
    TaskHandle,
    TaskResult,
)
```

## Required API Details

- `InMemoryBroker(sync_tasks_pool_size: int = 4, max_stored_results: int = 100, cast_types: bool = True, max_async_tasks: int = 30, max_async_tasks_jitter: int = 0, propagate_exceptions: bool = True, await_inplace: bool = False)` class constructor
  - `InMemoryBroker.task(self, task_func=None, *, task_name: str | None = None, **labels)`
  - `InMemoryBroker.find_task(self, task_name: str)`
  - `InMemoryBroker.wait_all(self) -> None`
- `DecoratedTask` class must be importable
  - `DecoratedTask.kiq(self, *args, **kwargs) -> TaskHandle`
  - `DecoratedTask.task_name` attribute must exist on instances
- `TaskHandle` class must be importable
  - `TaskHandle.wait_result(self) -> TaskResult`
  - `TaskHandle.is_ready(self) -> bool`
- `TaskResult` class must be importable
  - `TaskResult.return_value` attribute must exist on instances

## Required Behavior

- When an async or synchronous callable is decorated with `broker.task`, it is registered under a task name and the returned decorated task remains directly callable.
- Calling `await decorated_task.kiq(*args, **kwargs)` on a registered task schedules local in-memory execution and returns a task handle without requiring an external broker or service.
- Calling `await handle.wait_result()` waits for completion and returns a result object whose `return_value` is the callable result; `await handle.is_ready()` is false before completion when execution is pending and true afterward.
- Calling `await broker.wait_all()` waits for all currently scheduled in-memory tasks to finish, including both async and synchronous registered callables.
- The package exposes `InMemoryBroker` and the task, handle, and result members listed in the required API contract.
- The submitted package does not import the forbidden upstream package `taskiq` at runtime.

## Constraints

- Forbidden imports: `taskiq`.
- Do not implement Redis, NATS, and other external brokers.
- Do not implement worker processes and network transports.
- Do not implement schedulers, middleware, dependency injection, and lifecycle event hooks.
- Do not implement original taskiq import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — When an async or synchronous callable is decorated with `broker.task`, it is registered under a task name and the returned decorated task remains directly callable.
- **B002** — Calling `await decorated_task.kiq(*args, **kwargs)` on a registered task schedules local in-memory execution and returns a task handle without requiring an external broker or service.
- **B003** — Calling `await handle.wait_result()` waits for completion and returns a result object whose `return_value` is the callable result; `await handle.is_ready()` is false before completion when execution is pending and true afterward.
- **B004** — Calling `await broker.wait_all()` waits for all currently scheduled in-memory tasks to finish, including both async and synchronous registered callables.
- **B005** — The package exposes `InMemoryBroker` and the task, handle, and result members listed in the required API contract.
- **B006** — The submitted package does not import the forbidden upstream package `taskiq` at runtime.
<!-- featureliftbench:behavior-clauses:end -->
