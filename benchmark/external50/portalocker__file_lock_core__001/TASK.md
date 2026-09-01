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

- `Lock` accepts a local file path and yields a writable file handle from its context manager; `lock` and `unlock` acquire and release an advisory lock on an open file handle.
- `LOCK_EX`, `LOCK_SH`, and `LOCK_NB` are exposed as non-`None` lock flag constants.
- `Lock` accepts a numeric `timeout` argument and can acquire an available local file through the context-manager protocol.
- `LockException` is an exception type that subclasses `Exception`.
- The package exposes Lock/lock/unlock/LOCK_EX/LockException with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: portalocker.

## Constraints

- Forbidden imports: `portalocker`.
- Do not implement redis lock.
- Do not implement original portalocker import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — `Lock` accepts a local file path and yields a writable file handle from its context manager; `lock` and `unlock` acquire and release an advisory lock on an open file handle.
- **B002** — `LOCK_EX`, `LOCK_SH`, and `LOCK_NB` are exposed as non-`None` lock flag constants.
- **B003** — `Lock` accepts a numeric `timeout` argument and can acquire an available local file through the context-manager protocol.
- **B004** — `LockException` is an exception type that subclasses `Exception`.
- **B005** — The package exposes Lock/lock/unlock/LOCK_EX/LockException with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: portalocker.
<!-- featureliftbench:behavior-clauses:end -->
