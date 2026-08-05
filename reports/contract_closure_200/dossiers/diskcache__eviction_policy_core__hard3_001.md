# diskcache__eviction_policy_core__hard3_001

- release: `frozen_python150`
- lift: `Composite`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `5/11`

## Required API

- `featurelifted.EvictionPolicyPlanner` (class) `() -> 'None'`
- `featurelifted.EvictionPolicyPlanner.evict` (method) `(self, max_size: 'int', *, tag: 'str | None' = None) -> 'list[str]'`
- `featurelifted.EvictionPolicyPlanner.purge_expired` (method) `(self, now: 'float') -> 'list[str]'`
- `featurelifted.EvictionPolicyPlanner.set` (method) `(self, key: 'str', *, size: 'int' = 1, expire_at: 'float | None' = None, tag: 'str | None' = None) -> 'None'`
- `featurelifted.EvictionPolicyPlanner.total_size` (method) `(self) -> 'int'`
- `featurelifted.EvictionPolicyPlanner.touch` (method) `(self, key: 'str') -> 'None'`

## Public Behaviors

- **B001**: `touch(key)` updates access order for LRU decisions.
- **B002**: `evict(max_size, tag=...)` removes least-recently-used entries until under budget.
- **B003**: When purge_expired runs, expired entries are removed before size-based eviction and unexpired entries remain available.
- **B004**: The package exposes the required task API paths `featurelifted.EvictionPolicyPlanner`, `featurelifted.EvictionPolicyPlanner.evict`, `featurelifted.EvictionPolicyPlanner.purge_expired`, `featurelifted.EvictionPolicyPlanner.set`, `featurelifted.EvictionPolicyPlanner.total_size`, `featurelifted.EvictionPolicyPlanner.touch` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_evict_least_recently_used`

- mapping: `B001`
- API: `featurelifted.EvictionPolicyPlanner`
- risk: `none`
- A001 `assert` L11: `evicted == ['b']`

### `hidden_tests/test_hidden_contract.py::test_tag_filtered_eviction`

- mapping: `B002`
- API: `featurelifted.EvictionPolicyPlanner`
- risk: `none`
- A001 `assert` L10: `evicted == ['b']`
- A002 `assert` L11: `planner.total_size() == 2`

### `hidden_tests/test_hidden_contract.py::test_purge_expired_order`

- mapping: `B003`
- API: `featurelifted.EvictionPolicyPlanner`
- risk: `ordering_semantics`
- A001 `assert` L19: `removed == ['old']`

### `hidden_tests/test_hidden_contract.py::test_touch_updates_lru`

- mapping: `B001`
- API: `featurelifted.EvictionPolicyPlanner`
- risk: `state_mutation`
- A001 `assert` L28: `evicted == ['a']`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.EvictionPolicyPlanner`
- risk: `none`
- A001 `assert` L9: `isinstance(EvictionPolicyPlanner, type)`
- A002 `assert` L10: `hasattr(EvictionPolicyPlanner, 'evict')`
- A003 `assert` L11: `hasattr(EvictionPolicyPlanner, 'purge_expired')`
- A004 `assert` L12: `hasattr(EvictionPolicyPlanner, 'set')`
- A005 `assert` L13: `hasattr(EvictionPolicyPlanner, 'total_size')`
- A006 `assert` L14: `hasattr(EvictionPolicyPlanner, 'touch')`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `diskcache`
- source entrypoints: `diskcache.core.EvictionPolicyPlanner`
- oracle source files: `repo/diskcache/core.py`
- runtime dependencies: `none`
- oracle notes: In-memory eviction planner without sqlite backend.
