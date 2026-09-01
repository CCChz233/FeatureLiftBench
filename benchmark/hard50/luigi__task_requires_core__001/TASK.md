# FeatureLift Task: Local requires graph execution

Build a standalone local task runner that follows dependency graphs and uses filesystem targets to decide completion.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    build,
    LocalTarget,
    Task,
)
```

## Required API Details

- `Task()` class constructor
  - `Task.requires(self)`
  - `Task.output(self)`
  - `Task.run(self) -> None`
  - `Task.complete(self) -> bool`
- `LocalTarget(path: str)` class constructor
  - `LocalTarget.open(self, mode: str = 'r')`
  - `LocalTarget.exists(self) -> bool`
  - `LocalTarget.path` attribute must exist on instances
- `build(tasks, local_scheduler: bool = True, workers: int = 1, **kwargs) -> bool`

## Required Behavior

- Calling `build` with a task follows `requires` recursively through a single task or nested list, tuple, set, and dictionary containers, and each incomplete dependency runs before the task that requires it.
- When two branches of a dependency graph require the same task object, a successful local build executes that shared task no more than once before completing both branches and their join.
- `Task.complete()` returns whether every target from `output()` exists; a task with no outputs is incomplete, and already-complete tasks are skipped by `build`.
- `LocalTarget(path)` exposes that path, reports file existence, creates missing parent directories when opened for writing, and supports text reads and writes through context managers.
- A call to `build(..., local_scheduler=True, workers=1)` executes entirely in the current process without making HTTP requests or requiring a central scheduler and returns `True` after all requested tasks complete.
- The `Task` lifecycle methods, `LocalTarget` methods and path attribute, and `build` function are exported with the callable shapes stated in the required API.
- Runtime source inspection of the submitted Python files finds no import of the upstream `luigi` package.

## Constraints

- Forbidden imports: `luigi`.
- Do not implement parameters and command-line parsing.
- Do not implement remote or central scheduler communication.
- Do not implement multiple workers and process execution.
- Do not implement dynamic dependencies yielded from run.
- Do not implement runtime access to the source repository.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — Calling `build` with a task follows `requires` recursively through a single task or nested list, tuple, set, and dictionary containers, and each incomplete dependency runs before the task that requires it.
- **B002** — When two branches of a dependency graph require the same task object, a successful local build executes that shared task no more than once before completing both branches and their join.
- **B003** — `Task.complete()` returns whether every target from `output()` exists; a task with no outputs is incomplete, and already-complete tasks are skipped by `build`.
- **B004** — `LocalTarget(path)` exposes that path, reports file existence, creates missing parent directories when opened for writing, and supports text reads and writes through context managers.
- **B005** — A call to `build(..., local_scheduler=True, workers=1)` executes entirely in the current process without making HTTP requests or requiring a central scheduler and returns `True` after all requested tasks complete.
- **B006** — The `Task` lifecycle methods, `LocalTarget` methods and path attribute, and `build` function are exported with the callable shapes stated in the required API.
- **B007** — Runtime source inspection of the submitted Python files finds no import of the upstream `luigi` package.
<!-- featureliftbench:behavior-clauses:end -->
