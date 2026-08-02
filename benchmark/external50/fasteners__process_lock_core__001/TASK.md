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
- `InterProcessLock.release` callable must exist

## Required Behavior

- The extracted feature must support this observable behavior: InterProcessLock acquire/release. Required observable cases include acquire release; reacquire after release.
- The extracted feature must support this observable behavior: context manager acquires and releases. Required observable cases include context manager.
- The extracted feature must support this observable behavior: non-blocking acquire succeeds on a free lock. Required observable cases include nonblocking acquire free lock.
- Lock files are created under the provided path in temp directories during tests.
- The package exposes InterProcessLock with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: fasteners.

## Constraints

- Forbidden imports: `fasteners`.
- Do not implement redis locks.
- Do not implement original fasteners import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: InterProcessLock acquire/release. Required observable cases include acquire release; reacquire after release.
- **B002** — The extracted feature must support this observable behavior: context manager acquires and releases. Required observable cases include context manager.
- **B003** — The extracted feature must support this observable behavior: non-blocking acquire succeeds on a free lock. Required observable cases include nonblocking acquire free lock.
- **B004** — Lock files are created under the provided path in temp directories during tests.
- **B005** — The package exposes InterProcessLock with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: fasteners.
<!-- featureliftbench:behavior-clauses:end -->
