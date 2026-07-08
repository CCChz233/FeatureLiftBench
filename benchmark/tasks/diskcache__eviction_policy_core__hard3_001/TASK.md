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
