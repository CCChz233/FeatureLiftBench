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

- `DictCache` class must be importable
  - `DictCache.get` callable must exist
  - `DictCache.set` callable must exist
  - `DictCache.delete` callable must exist
- `BaseCache` class must be importable
- `ExpiresAfter` class must be importable
- `Serializer` class must be importable
- `CacheController` class must be importable
  - `CacheController.cache` attribute must exist on instances

## Required Behavior

- The extracted feature must support this observable behavior: DictCache get/set/delete. Required observable cases include dict cache roundtrip.
- The extracted feature must support this observable behavior: ExpiresAfter and Serializer construction. Required observable cases include expires after construct; serializer construct; expires after days hours; serializer serde version.
- The extracted feature must support this observable behavior: CacheController wraps a cache and DictCache subclasses BaseCache. Required observable cases include cache controller construct; base cache interface.
- No live HTTP is required; tests use in-memory DictCache only.
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

- **B001** — The extracted feature must support this observable behavior: DictCache get/set/delete. Required observable cases include dict cache roundtrip.
- **B002** — The extracted feature must support this observable behavior: ExpiresAfter and Serializer construction. Required observable cases include expires after construct; serializer construct; expires after days hours; serializer serde version.
- **B003** — The extracted feature must support this observable behavior: CacheController wraps a cache and DictCache subclasses BaseCache. Required observable cases include cache controller construct; base cache interface.
- **B004** — No live HTTP is required; tests use in-memory DictCache only.
- **B005** — The package exposes DictCache/BaseCache/ExpiresAfter/Serializer/CacheController with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: cachecontrol.
<!-- featureliftbench:behavior-clauses:end -->
