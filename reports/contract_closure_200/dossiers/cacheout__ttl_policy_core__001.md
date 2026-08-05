# cacheout__ttl_policy_core__001

- release: `external50`
- lift: `Direct`
- coupling: `config_environment_coupling`
- strict validation: `PASS`
- tests/assertions: `6/12`

## Required API

- `featurelifted.Cache` (class) `(maxsize: int = 256, ttl: float = 0, timer=None, default=None, enable_stats: bool = False)`
- `featurelifted.Cache.set` (method) `(key, value, ttl=None) -> None`
- `featurelifted.Cache.get` (method) `(key, default=None)`
- `featurelifted.Cache.delete` (method) `(key) -> int`
- `featurelifted.Cache.configure` (method) `(**kwargs) -> None`
- `featurelifted.LRUCache` (class) `(maxsize: int = 256, ttl: float = 0, timer=None, default=None, enable_stats: bool = False)`

## Public Behaviors

- **B001**: Cache stores, retrieves, and deletes values while honoring constructor and configure defaults.
- **B002**: TTL expiration uses the injected timer deterministically and supports per-entry overrides.
- **B003**: LRUCache evicts the least recently accessed entry when maxsize is exceeded.
- **B004**: The submitted package does not import cacheout or read the upstream repository at runtime.

## Tests

### `public_tests/test_public_api.py::test_cache_roundtrip_and_delete`

- mapping: `B001`
- API: `featurelifted.Cache`
- risk: `state_mutation`
- A001 `assert` L12: `cache.get('a') == 1`
- A002 `assert` L13: `cache.delete('a') == 1`
- A003 `assert` L14: `cache.get('a') is None`

### `public_tests/test_public_api.py::test_ttl_uses_injected_timer`

- mapping: `B002`
- API: `featurelifted.Cache`
- risk: `none`
- A001 `assert` L22: `cache.get('a') == 1`
- A002 `assert` L24: `cache.get('a') is None`

### `hidden_tests/test_hidden_behavior.py::test_configure_changes_default_ttl`

- mapping: `B001, B002`
- API: `featurelifted.Cache`
- risk: `none`
- A001 `assert` L13: `not cache.has('x')`

### `hidden_tests/test_hidden_behavior.py::test_lru_touch_controls_eviction`

- mapping: `B003`
- API: `featurelifted.LRUCache`
- risk: `none`
- A001 `assert` L19: `cache.get('a') == 1`
- A002 `assert` L21: `'a' in cache and 'b' not in cache and ('c' in cache)`

### `hidden_tests/test_hidden_behavior.py::test_required_api_surface`

- mapping: `B003`
- API: `featurelifted.Cache, featurelifted.LRUCache`
- risk: `none`
- A001 `assert` L26: `isinstance(Cache, type)`
- A002 `assert` L27: `isinstance(LRUCache, type)`
- A003 `assert` L28: `all((callable(getattr(Cache, n)) for n in ('set', 'get', 'delete', 'configure')))`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B004`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L37: `not pattern.search(path.read_text(encoding='utf-8'))`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `cacheout`
- source entrypoints: `none`
- oracle source files: `src/cacheout/cache.py, src/cacheout/lru.py`
- runtime dependencies: `none`
- oracle notes: Balanced Python-200 replacement slot cache-direct-config-01; offline reference only.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
