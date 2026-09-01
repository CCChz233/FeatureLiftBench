# FeatureLift Task: cachecontrol heuristic store

Extract a task-scoped subset of `cachecontrol` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    BaseCache,
    CacheController,
    DictCache,
    ExpiresAfter,
    Serializer,
)
```

## Required API Details

- `DictCache(init_dict=None)` class constructor
  - `DictCache.get(self, key: str) -> bytes | None`
  - `DictCache.set(self, key: str, value: bytes, expires=None) -> None`
  - `DictCache.delete(self, key: str) -> None`
- `BaseCache` class must be importable
- `ExpiresAfter(**timedelta_kwargs)` class constructor
- `Serializer()` class constructor
- `CacheController(cache=None, cache_etags=True, serializer=None, status_codes=None)` class constructor
  - `CacheController.cache` attribute must exist on instances

## Required Behavior

- A `DictCache` is a `BaseCache`; after `set` stores bytes under a key, `get` returns those bytes, and after `delete` removes the key, `get` returns `None`.
- Constructing `ExpiresAfter` with day and hour keyword arguments creates a heuristic whose `delta` represents that combined duration.
- When `CacheController` is constructed with a `DictCache`, its public `cache` attribute refers to a usable cache instance.
- Constructing `Serializer` requires no arguments and exposes a non-empty `serde_version` identifying its serialization format.
- The package exposes DictCache/BaseCache/ExpiresAfter/Serializer/CacheController with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: cachecontrol.

## Constraints

- Forbidden imports: `cachecontrol`.
- Do not implement requests Session integration.
- Do not implement FileCache.
- Do not implement network.
- Do not implement original cachecontrol import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — A `DictCache` is a `BaseCache`; after `set` stores bytes under a key, `get` returns those bytes, and after `delete` removes the key, `get` returns `None`.
- **B002** — Constructing `ExpiresAfter` with day and hour keyword arguments creates a heuristic whose `delta` represents that combined duration.
- **B003** — When `CacheController` is constructed with a `DictCache`, its public `cache` attribute refers to a usable cache instance.
- **B004** — Constructing `Serializer` requires no arguments and exposes a non-empty `serde_version` identifying its serialization format.
- **B005** — The package exposes DictCache/BaseCache/ExpiresAfter/Serializer/CacheController with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: cachecontrol.
<!-- featureliftbench:behavior-clauses:end -->
