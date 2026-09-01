# FeatureLift Task: Configurable TTL and LRU cache policy

Extract Cache and LRUCache policy behavior with deterministic timers and runtime configuration.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    Cache,
    LRUCache,
)
```

## Required API Details

- `Cache(maxsize: int = 256, ttl: float = 0, timer=None, default=None, enable_stats: bool = False)` class constructor
  - `Cache.set(key, value, ttl=None) -> None`
  - `Cache.get(key, default=None)`
  - `Cache.delete(key) -> int`
  - `Cache.configure(**kwargs) -> None`
- `LRUCache(maxsize: int = 256, ttl: float = 0, timer=None, default=None, enable_stats: bool = False)` class constructor

## Required Behavior

- `Cache.set` stores a key/value pair, `get` returns the stored value while it is live, and `delete` returns 1 for a removed key after which `get` returns the configured default.
- Given an injected callable timer and a positive default TTL, a cached entry remains available before its deadline and is unavailable when the timer reaches the deadline.
- Calling `Cache.configure(ttl=...)` changes the default TTL used by entries stored afterward.
- When inserting beyond `LRUCache.maxsize`, the least recently accessed entry is evicted, and a successful `get` refreshes an entry's recency.
- The package exposes the required task API paths `featurelifted.Cache`, `featurelifted.Cache.set`, `featurelifted.Cache.get`, `featurelifted.Cache.delete`, `featurelifted.Cache.configure`, and `featurelifted.LRUCache` with the kinds and callable signatures listed in this contract.
- the submitted package does not import forbidden upstream packages: cacheout.

## Constraints

- Forbidden imports: `cacheout`.
- Do not implement async wrappers.
- Do not implement global cache manager.
- Do not implement random-replacement policies.
- Do not implement original cacheout import at runtime.

## Public vs Hidden Tests

Public tests cover common use. Hidden tests cover documented edge, configuration, state, API-surface, and isolation behavior only.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — `Cache.set` stores a key/value pair, `get` returns the stored value while it is live, and `delete` returns 1 for a removed key after which `get` returns the configured default.
- **B002** — Given an injected callable timer and a positive default TTL, a cached entry remains available before its deadline and is unavailable when the timer reaches the deadline.
- **B003** — Calling `Cache.configure(ttl=...)` changes the default TTL used by entries stored afterward.
- **B004** — When inserting beyond `LRUCache.maxsize`, the least recently accessed entry is evicted, and a successful `get` refreshes an entry's recency.
- **B005** — The package exposes the required task API paths `featurelifted.Cache`, `featurelifted.Cache.set`, `featurelifted.Cache.get`, `featurelifted.Cache.delete`, `featurelifted.Cache.configure`, and `featurelifted.LRUCache` with the kinds and callable signatures listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: cacheout.
<!-- featureliftbench:behavior-clauses:end -->
