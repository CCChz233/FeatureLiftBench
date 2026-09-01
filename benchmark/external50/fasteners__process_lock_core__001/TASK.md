# FeatureLift Task: fasteners process lock

Extract a task-scoped subset of `fasteners` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    InterProcessLock,
)
```

## Required API Details

- `InterProcessLock` class must be importable
- `InterProcessLock.acquire(blocking: bool = True) -> bool`
- `InterProcessLock.release() -> None`

## Required Behavior

- `InterProcessLock` accepts a filesystem path, acquires an available lock either through `acquire()` or as a context manager, and releases the lock through `release()` or context exit.
- After an acquired `InterProcessLock` is released, the same lock object can acquire that path again and returns `True`.
- `InterProcessLock.acquire(blocking=False)` returns `True` when the requested lock is currently free.
- `InterProcessLock` operates on a caller-provided local path without requiring the lock file to exist before acquisition.
- The package exposes InterProcessLock with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: fasteners.

## Constraints

- Forbidden imports: `fasteners`.
- Do not implement redis locks.
- Do not implement original fasteners import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — `InterProcessLock` accepts a filesystem path, acquires an available lock either through `acquire()` or as a context manager, and releases the lock through `release()` or context exit.
- **B002** — After an acquired `InterProcessLock` is released, the same lock object can acquire that path again and returns `True`.
- **B003** — `InterProcessLock.acquire(blocking=False)` returns `True` when the requested lock is currently free.
- **B004** — `InterProcessLock` operates on a caller-provided local path without requiring the lock file to exist before acquisition.
- **B005** — The package exposes InterProcessLock with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: fasteners.
<!-- featureliftbench:behavior-clauses:end -->
