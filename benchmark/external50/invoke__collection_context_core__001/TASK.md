# FeatureLift Task: invoke collection context

Extract a task-scoped subset of `invoke` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    Collection,
    Context,
    MockContext,
    task,
    UnexpectedExit,
)
```

## Required API Details

- `task(*args, **kwargs)`
- `Collection(*args, **kwargs)` class constructor
  - `Collection.add_task(self, task, name=None, aliases=None, default=None) -> None`
  - `Collection.add_collection(self, coll, name=None, default=None) -> None`
- `Context(config=None, overrides=None, defaults=None, remainder='')` class constructor
- `MockContext(**kwargs)` class constructor
  - `MockContext.run(*args, **kwargs)`
- `UnexpectedExit` class must be importable

## Required Behavior

- When a `task`-decorated function is added to a `Collection`, retrieving it by name and calling it with a `Context` forwards positional and keyword arguments and returns the function result.
- Tasks accept context-compatible objects as their first argument; with `MockContext(run=True)`, a task may call `run` without launching a shell and the mock records that call.
- When a named child collection contains a task, the parent resolves and invokes that task through its dotted name, and an `UnexpectedExit` raised by a task propagates with that exception type.
- Using `Collection.__getitem__` with a direct task name or a dotted child-collection task name returns the corresponding callable task.
- The package exposes task/Collection/Context/MockContext/UnexpectedExit with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: invoke.

## Constraints

- Forbidden imports: `invoke`.
- Do not implement real SSH fabric.
- Do not implement original invoke import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — When a `task`-decorated function is added to a `Collection`, retrieving it by name and calling it with a `Context` forwards positional and keyword arguments and returns the function result.
- **B002** — Tasks accept context-compatible objects as their first argument; with `MockContext(run=True)`, a task may call `run` without launching a shell and the mock records that call.
- **B003** — When a named child collection contains a task, the parent resolves and invokes that task through its dotted name, and an `UnexpectedExit` raised by a task propagates with that exception type.
- **B004** — Using `Collection.__getitem__` with a direct task name or a dotted child-collection task name returns the corresponding callable task.
- **B005** — The package exposes task/Collection/Context/MockContext/UnexpectedExit with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: invoke.
<!-- featureliftbench:behavior-clauses:end -->
