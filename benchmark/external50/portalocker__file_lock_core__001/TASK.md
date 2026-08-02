# FeatureLift Task: portalocker file lock

Extract a task-scoped subset of `portalocker` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    Lock,
    lock,
    LOCK_EX,
    LOCK_NB,
    LOCK_SH,
    LockException,
    unlock,
)
```

## Required API Details

- `lock(file, flags=LOCK_EX)`
- `unlock(file)`
- `Lock` class must be importable
- `LOCK_EX` constant must exist
- `LOCK_SH` constant must exist
- `LOCK_NB` constant must exist
- `LockException` class must be importable

## Required Behavior

- The extracted feature must support this observable behavior: Lock context manager and lock/unlock on file handles. Required observable cases include lock context manager; lock unlock functions.
- The extracted feature must support this observable behavior: LOCK_EX and related constants are exposed. Required observable cases include lock constants.
- The extracted feature must support this observable behavior: Lock accepts timeout and LockException exists. Required observable cases include lock timeout; lock exception type.
- Tests use local temp files only; no network resources.
- The package exposes Lock/lock/unlock/LOCK_EX/LockException with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: portalocker.

## Constraints

- Forbidden imports: `portalocker`.
- Do not implement redis lock.
- Do not implement original portalocker import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: Lock context manager and lock/unlock on file handles. Required observable cases include lock context manager; lock unlock functions.
- **B002** — The extracted feature must support this observable behavior: LOCK_EX and related constants are exposed. Required observable cases include lock constants.
- **B003** — The extracted feature must support this observable behavior: Lock accepts timeout and LockException exists. Required observable cases include lock timeout; lock exception type.
- **B004** — Tests use local temp files only; no network resources.
- **B005** — The package exposes Lock/lock/unlock/LOCK_EX/LockException with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: portalocker.
<!-- featureliftbench:behavior-clauses:end -->
