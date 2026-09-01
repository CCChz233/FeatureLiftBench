# FeatureLift Task: freezegun freeze time

Extract a task-scoped subset of `freezegun` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    freeze_time,
    FrozenDateTimeFactory,
    StepTickTimeFactory,
    TickingDateTimeFactory,
)
```

## Required API Details

- `freeze_time(time_to_freeze=None, tz_offset=0, ignore=None, tick: bool = False, as_arg: bool = False, as_kwarg: str = '', auto_tick_seconds: float = 0, real_asyncio: bool = False)`
- `FrozenDateTimeFactory` class must be importable
  - `FrozenDateTimeFactory.tick(delta: timedelta | float = timedelta(seconds=1)) -> None`
  - `FrozenDateTimeFactory.move_to(target_datetime) -> None`
- `TickingDateTimeFactory` class must be importable
  - `TickingDateTimeFactory.tick(delta: timedelta = timedelta(seconds=1)) -> None`
  - `TickingDateTimeFactory.move_to(target_datetime) -> None`
- `StepTickTimeFactory` class must be importable
  - `StepTickTimeFactory.tick(delta: timedelta | float = timedelta(seconds=1)) -> None`
  - `StepTickTimeFactory.move_to(target_datetime) -> None`

## Required Behavior

- freeze_time accepts date/time text as a context manager or decorator, makes datetime.now() report the requested time, and restores the real clock after the scope exits.
- The factory returned by an active freeze exposes tick(delta=...) and move_to(target_datetime); these operations advance or replace the time subsequently observed through datetime.now().
- The package exposes freeze_time and the three factory classes, including each factory's tick and move_to methods, with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: freezegun.

## Constraints

- Forbidden imports: `freezegun`.
- Do not implement C extension clock patching.
- Do not implement original freezegun import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — freeze_time accepts date/time text as a context manager or decorator, makes datetime.now() report the requested time, and restores the real clock after the scope exits.
- **B002** — The factory returned by an active freeze exposes tick(delta=...) and move_to(target_datetime); these operations advance or replace the time subsequently observed through datetime.now().
- **B003** — The package exposes freeze_time and the three factory classes, including each factory's tick and move_to methods, with the kinds listed in this contract.
- **B004** — the submitted package does not import forbidden upstream packages: freezegun.
<!-- featureliftbench:behavior-clauses:end -->
