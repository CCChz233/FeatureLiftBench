# FeatureLift Task: EvictionPolicyPlanner

Extract diskcache eviction planning into `featurelifted`.

## Target API

```python
from featurelifted import EvictionPolicyPlanner
```

## Required Behavior

- `EvictionPolicyPlanner` tracks entry sizes, tags, and access order in memory.
- `evict(max_size, tag=...)` removes least-recently-used entries until under budget.
- `purge_expired(now)` removes expired entries in stable order.
- `touch(key)` updates access order for LRU decisions.

## Constraints

- Forbidden imports: `diskcache`.
- No sqlite or filesystem I/O.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — LRU eviction planning
- **B002** — tag filtering
- **B003** — expiration purge
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: diskcache
<!-- featureliftbench:behavior-clauses:end -->
