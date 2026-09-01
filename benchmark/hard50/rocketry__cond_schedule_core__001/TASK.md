# FeatureLift Task: Condition schedule without a long loop

Build a standalone `featurelifted` package providing Rocketry-style `true`/`false` conditions and a `Session` that can register and run one in-process task without starting a long-running scheduler loop.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    false,
    Session,
    true,
)
```

## Required API Details

- `Session(config=None)` class constructor
  - `Session.create_task(self, **kwargs)`
  - `Session.run(self, *task_names: str, execution=None, obey_cond=False)`
- `true` constant must exist
- `false` constant must exist

## Required Behavior

- `true` is a condition that evaluates true and `false` evaluates false. Combining them with `&` is false and combining them with `|` is true.
- A `Session` constructed with `execution='main'` and `cycle_sleep=0` can register a function via `create_task(start_cond=true, name=..., execution='main')` and `run(name, obey_cond=True, execution='main')` executes that function once without leaving a long-running scheduler loop.
- When `start_cond` is `false` and `run(..., obey_cond=True)` is used, the registered function is not called.
- A task whose `start_cond` is `true | false` does run under `obey_cond=True`. Tests construct their own `Session` rather than starting the import-time default scheduler.
- The package exposes `Session`, `true`, and `false` with `create_task` and `run` as listed in this contract.
- The submitted package source does not import the forbidden upstream package `rocketry`.

## Constraints

- Forbidden imports: `rocketry`.
- Do not implement production scheduler loops.
- Do not implement remote execution.
- Do not implement process or thread execution backends.
- Do not implement runtime import of rocketry.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — `true` is a condition that evaluates true and `false` evaluates false. Combining them with `&` is false and combining them with `|` is true.
- **B002** — A `Session` constructed with `execution='main'` and `cycle_sleep=0` can register a function via `create_task(start_cond=true, name=..., execution='main')` and `run(name, obey_cond=True, execution='main')` executes that function once without leaving a long-running scheduler loop.
- **B003** — When `start_cond` is `false` and `run(..., obey_cond=True)` is used, the registered function is not called.
- **B004** — A task whose `start_cond` is `true | false` does run under `obey_cond=True`. Tests construct their own `Session` rather than starting the import-time default scheduler.
- **B005** — The package exposes `Session`, `true`, and `false` with `create_task` and `run` as listed in this contract.
- **B006** — The submitted package source does not import the forbidden upstream package `rocketry`.
<!-- featureliftbench:behavior-clauses:end -->
