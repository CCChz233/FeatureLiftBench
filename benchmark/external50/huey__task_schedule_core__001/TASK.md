# FeatureLift Task: huey task schedule

Extract a task-scoped subset of `huey` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    crontab,
    MemoryHuey,
)
```

## Required API Details

- `MemoryHuey(name='huey', results=True, store_none=False, utc=True, immediate=False, serializer=None, compression=False, use_zlib=False)` class constructor
  - `MemoryHuey.task(self, retries=0, retry_delay=0, retry_backoff=0, priority=None, context=False, name=None, expires=None, timeout=None, **kwargs)`
  - `MemoryHuey.pending_count(self) -> int`
  - `MemoryHuey.flush(self) -> None`
- `crontab(minute='*', hour='*', day='*', month='*', day_of_week='*', strict=False)`

## Required Behavior

- When a function decorated by `MemoryHuey.task()` is called, one task is enqueued; after `dequeue` and `execute`, the returned result handle's nonblocking `get` returns the function result.
- A `crontab` schedule built with a step expression is callable and returns true only for matching datetimes; independently enqueued task calls retain their own arguments and results.
- After one or more decorated task calls are queued, calling `flush` removes all pending work so `pending_count` returns zero.
- Before a queued task is flushed or dequeued, `pending_count` reports at least one pending item.
- The package exposes MemoryHuey and crontab with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: huey.

## Constraints

- Forbidden imports: `huey`.
- Do not implement RedisHuey.
- Do not implement consumer process.
- Do not implement original huey import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — When a function decorated by `MemoryHuey.task()` is called, one task is enqueued; after `dequeue` and `execute`, the returned result handle's nonblocking `get` returns the function result.
- **B002** — A `crontab` schedule built with a step expression is callable and returns true only for matching datetimes; independently enqueued task calls retain their own arguments and results.
- **B003** — After one or more decorated task calls are queued, calling `flush` removes all pending work so `pending_count` returns zero.
- **B004** — Before a queued task is flushed or dequeued, `pending_count` reports at least one pending item.
- **B005** — The package exposes MemoryHuey and crontab with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: huey.
<!-- featureliftbench:behavior-clauses:end -->
