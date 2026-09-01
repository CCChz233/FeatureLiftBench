# FeatureLift Task: Fixed-window memory rate limiter

Build a standalone `featurelifted` package providing in-memory fixed-window rate limiting from parsed limit strings.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    FixedWindowRateLimiter,
    MemoryStorage,
    parse,
)
```

## Required API Details

- `MemoryStorage(uri: str | None = None, wrap_exceptions: bool = False, **_)` class constructor
  - `MemoryStorage.__init__(self, uri: str | None = None, wrap_exceptions: bool = False, **_)`
  - `MemoryStorage.incr(self, key: str, expiry: float, amount: int = 1) -> int`
  - `MemoryStorage.get(self, key: str) -> int`
- `FixedWindowRateLimiter(storage)` class constructor
  - `FixedWindowRateLimiter.__init__(self, storage)`
  - `FixedWindowRateLimiter.hit(self, item, *identifiers: str, cost: int = 1) -> bool`
  - `FixedWindowRateLimiter.get_window_stats(self, item, *identifiers: str) -> WindowStats`
- `parse(limit_string: str)`

## Required Behavior

- After `parse` builds a limit item, `FixedWindowRateLimiter.hit` against `MemoryStorage` returns True until the parsed amount is exhausted in that window, then False.
- After a window is exhausted, `get_window_stats` reports `remaining == 0` for the same identifiers.
- Hits for distinct identifier strings are counted independently against the same limiter and limit item.
- `MemoryStorage.incr` increases a key by the given amount and `get` returns 0 for a missing key and the stored count afterwards.
- The package exposes `MemoryStorage`, `FixedWindowRateLimiter`, `parse`, `hit`, `get_window_stats`, `incr`, and `get` with the signatures listed in this contract.
- The submitted package source does not import the forbidden upstream package `limits`.

## Constraints

- Forbidden imports: `limits`.
- Do not implement Redis storage.
- Do not implement Memcached storage.
- Do not implement MongoDB storage.
- Do not implement runtime import of limits.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — After `parse` builds a limit item, `FixedWindowRateLimiter.hit` against `MemoryStorage` returns True until the parsed amount is exhausted in that window, then False.
- **B002** — After a window is exhausted, `get_window_stats` reports `remaining == 0` for the same identifiers.
- **B003** — Hits for distinct identifier strings are counted independently against the same limiter and limit item.
- **B004** — `MemoryStorage.incr` increases a key by the given amount and `get` returns 0 for a missing key and the stored count afterwards.
- **B005** — The package exposes `MemoryStorage`, `FixedWindowRateLimiter`, `parse`, `hit`, `get_window_stats`, `incr`, and `get` with the signatures listed in this contract.
- **B006** — The submitted package source does not import the forbidden upstream package `limits`.
<!-- featureliftbench:behavior-clauses:end -->
