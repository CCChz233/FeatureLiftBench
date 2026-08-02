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

- Cache stores, retrieves, and deletes values while honoring constructor and configure defaults.
- TTL expiration uses the injected timer deterministically and supports per-entry overrides.
- LRUCache evicts the least recently accessed entry when maxsize is exceeded.
- The submitted package does not import cacheout or read the upstream repository at runtime.

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

- **B001** — Cache stores, retrieves, and deletes values while honoring constructor and configure defaults.
- **B002** — TTL expiration uses the injected timer deterministically and supports per-entry overrides.
- **B003** — LRUCache evicts the least recently accessed entry when maxsize is exceeded.
- **B004** — The submitted package does not import cacheout or read the upstream repository at runtime.
<!-- featureliftbench:behavior-clauses:end -->
