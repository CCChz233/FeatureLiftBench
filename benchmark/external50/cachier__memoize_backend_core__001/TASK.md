# FeatureLift Task: Memoization decorator and backend policy

Extract cachier decorator behavior with deterministic memory caching, per-call overrides, and global policy controls.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    cachier,
    disable_caching,
    enable_caching,
    get_default_params,
    set_default_params,
)
```

## Required API Details

- `cachier(*, backend='pickle', stale_after=..., next_time=False, cache_dir=None, ...)`
- `set_default_params(**params) -> None`
- `get_default_params() -> dict`
- `enable_caching() -> None`
- `disable_caching() -> None`

## Required Behavior

- The memory backend memoizes by arguments and exposes clear_cache and precache_value on wrapped callables.
- Per-call skip-cache and overwrite-cache controls bypass or replace an existing entry deterministically.
- Global enable and disable controls affect decorated functions and can be restored between tests.
- The submitted package uses only locked backend dependencies and does not import cachier.

## Constraints

- Forbidden imports: `cachier`.
- Do not implement MongoDB, Redis, SQL, and S3 services.
- Do not implement background timing assertions.
- Do not implement network access.
- Do not implement original cachier import at runtime.

## Public vs Hidden Tests

Public tests cover common use. Hidden tests cover documented edge, configuration, state, API-surface, and isolation behavior only.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The memory backend memoizes by arguments and exposes clear_cache and precache_value on wrapped callables.
- **B002** — Per-call skip-cache and overwrite-cache controls bypass or replace an existing entry deterministically.
- **B003** — Global enable and disable controls affect decorated functions and can be restored between tests.
- **B004** — The submitted package uses only locked backend dependencies and does not import cachier.
<!-- featureliftbench:behavior-clauses:end -->
