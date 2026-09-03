# FeatureLift Task: Memory session and cache

Build a standalone `featurelifted` package providing Beaker-style in-memory sessions and cache namespaces, including decorator get-or-create, without memcached.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    CacheManager,
    MemoryNamespaceManager,
    Session,
)
```

## Required API Details

- `Session(request, id=None, use_cookies=True, type=None, **kwargs)` class constructor
  - `Session.save(self, accessed_only=False)`
  - `Session.load(self)`
  - `Session.__setitem__(self, key, value, /)`
  - `Session.get(self, key, default=None, /)`
  - `Session.id` attribute must exist on instances
- `CacheManager(**kwargs)` class constructor
  - `CacheManager.get_cache(self, name, **kwargs)`
  - `CacheManager.cache(self, *args, **kwargs)`
- `MemoryNamespaceManager(namespace, **kwargs)` class constructor

## Required Behavior

- A memory `Session` created with `use_cookies=False` stores values like a mapping; after `save()`, a second `Session` constructed with the same `id` can read those values.
- `CacheManager(type='memory').get_cache(name)` supports `put` then `get` for the same key in that named namespace.
- `CacheManager.cache` used as a decorator memoizes a function so a second call with the same arguments does not re-run the wrapped body.
- Sessions with different ids do not share keys. The memory backend does not contact memcached.
- The package exposes `Session`, `CacheManager`, and `MemoryNamespaceManager` as listed in this contract.
- The submitted package source does not import the forbidden upstream package `beaker`.

## Constraints

- Forbidden imports: `beaker`.
- Do not implement memcached namespaces.
- Do not implement SQLAlchemy or database namespaces.
- Do not implement cookie cryptography beyond the memory session path.
- Do not implement runtime import of beaker.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — A memory `Session` created with `use_cookies=False` stores values like a mapping; after `save()`, a second `Session` constructed with the same `id` can read those values.
- **B002** — `CacheManager(type='memory').get_cache(name)` supports `put` then `get` for the same key in that named namespace.
- **B003** — `CacheManager.cache` used as a decorator memoizes a function so a second call with the same arguments does not re-run the wrapped body.
- **B004** — Sessions with different ids do not share keys. The memory backend does not contact memcached.
- **B005** — The package exposes `Session`, `CacheManager`, and `MemoryNamespaceManager` as listed in this contract.
- **B006** — The submitted package source does not import the forbidden upstream package `beaker`.
<!-- featureliftbench:behavior-clauses:end -->
