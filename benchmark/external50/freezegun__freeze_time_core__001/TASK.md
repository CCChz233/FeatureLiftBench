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

- `freeze_time(time_to_freeze=None, tick: bool = False, ...)`
- `FrozenDateTimeFactory` class must be importable
  - `FrozenDateTimeFactory.tick` callable must exist
  - `FrozenDateTimeFactory.move_to` callable must exist
- `TickingDateTimeFactory` class must be importable
  - `TickingDateTimeFactory.tick` callable must exist
  - `TickingDateTimeFactory.move_to` callable must exist
- `StepTickTimeFactory` class must be importable
  - `StepTickTimeFactory.tick` callable must exist
  - `StepTickTimeFactory.move_to` callable must exist

## Required Behavior

- The extracted feature must support this observable behavior: freeze_time context manager and decorator. Required observable cases include freeze context manager; freeze decorator; unfrozen after context.
- The extracted feature must support this observable behavior: tick and move_to advance frozen time. Required observable cases include tick moves time; move to.
- Real clock resumes after the freeze context exits.
- python-dateutil is the only allowed third-party dependency.
- The package exposes freeze_time with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: freezegun.

## Constraints

- Forbidden imports: `freezegun`.
- Do not implement C extension clock patching.
- Do not implement original freezegun import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: freeze_time context manager and decorator. Required observable cases include freeze context manager; freeze decorator; unfrozen after context.
- **B002** — The extracted feature must support this observable behavior: tick and move_to advance frozen time. Required observable cases include tick moves time; move to.
- **B003** — Real clock resumes after the freeze context exits.
- **B004** — python-dateutil is the only allowed third-party dependency.
- **B005** — The package exposes freeze_time with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: freezegun.
<!-- featureliftbench:behavior-clauses:end -->
