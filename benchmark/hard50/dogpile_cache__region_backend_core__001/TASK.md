# FeatureLift Task: Dogpile cache region and memory backend core

Extract the stateful in-process cache-region core into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    CacheRegion,
    make_region,
    NO_VALUE,
)
```

## Required API Details

- `make_region(*args, **kwargs) -> CacheRegion`
- `CacheRegion(name: str | None = None, function_key_generator=<default>, function_multi_key_generator=<default>, key_mangler=None, serializer=None, deserializer=None, async_creation_runner=None)` class constructor
  - `CacheRegion.configure(self, backend: str, expiration_time: float | datetime.timedelta | None = None, arguments: dict | None = None, _config_argument_dict=None, _config_prefix=None, wrap=(), replace_existing_backend: bool = False, region_invalidator=None) -> CacheRegion`
  - `CacheRegion.get(self, key: str, expiration_time: float | None = None, ignore_expiration: bool = False)`
  - `CacheRegion.get_or_create(self, key: str, creator, expiration_time: float | None = None, should_cache_fn=None, creator_args=None)`
  - `CacheRegion.invalidate(self, hard: bool = True) -> None`
  - `CacheRegion.is_configured` attribute must exist on instances
  - `CacheRegion.name` attribute must exist on instances
- `NO_VALUE` constant must exist

## Required Behavior

- `make_region` returns an unconfigured `CacheRegion`, forwards constructor arguments such as `name`, and `configure('dogpile.cache.memory')` configures the in-process memory backend, returns the same region, and makes `is_configured` true.
- For a configured memory region, the first `get_or_create(key, creator)` call for a missing key calls the creator and caches its result; later calls for that key return the cached result without calling later creators, while different keys are independent.
- `CacheRegion.get` returns the singleton `NO_VALUE` sentinel for a missing key, and `NO_VALUE` is false in boolean context while remaining distinct from a cached `None` value.
- After a value has been cached, `CacheRegion.invalidate()` causes `get` to report `NO_VALUE` for that stale value and the next `get_or_create` for the same key to invoke its creator and cache the replacement.
- Configuring an already configured region without `replace_existing_backend=True` raises an exception; passing that flag permits replacement with a fresh memory backend.
- The package exposes `make_region`, `CacheRegion`, `NO_VALUE`, and the required `CacheRegion` members with the kinds and callable signatures listed in this contract.

## Constraints

- Forbidden imports: `dogpile`.
- Do not implement Redis, Memcached, Valkey, DBM, file, and null backends.
- Do not implement distributed locking and cross-process invalidation.
- Do not implement decorator APIs, multi-key APIs, serializers, backend proxies, and plugin registration.
- Do not implement the original dogpile package at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — `make_region` returns an unconfigured `CacheRegion`, forwards constructor arguments such as `name`, and `configure('dogpile.cache.memory')` configures the in-process memory backend, returns the same region, and makes `is_configured` true.
- **B002** — For a configured memory region, the first `get_or_create(key, creator)` call for a missing key calls the creator and caches its result; later calls for that key return the cached result without calling later creators, while different keys are independent.
- **B003** — `CacheRegion.get` returns the singleton `NO_VALUE` sentinel for a missing key, and `NO_VALUE` is false in boolean context while remaining distinct from a cached `None` value.
- **B004** — After a value has been cached, `CacheRegion.invalidate()` causes `get` to report `NO_VALUE` for that stale value and the next `get_or_create` for the same key to invoke its creator and cache the replacement.
- **B005** — Configuring an already configured region without `replace_existing_backend=True` raises an exception; passing that flag permits replacement with a fresh memory backend.
- **B006** — The package exposes `make_region`, `CacheRegion`, `NO_VALUE`, and the required `CacheRegion` members with the kinds and callable signatures listed in this contract.
<!-- featureliftbench:behavior-clauses:end -->
