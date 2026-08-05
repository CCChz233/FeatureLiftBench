# cachetools__cache_eviction_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `11/39`

## Required API

- `featurelifted.LRUCache` (class) `(maxsize, getsizeof=None)`
- `featurelifted.LRUCache.maxsize` (attribute)
- `featurelifted.TTLCache` (class) `(maxsize, ttl, timer=<built-in function monotonic>, getsizeof=None)`
- `featurelifted.LFUCache` (class) `(maxsize, getsizeof=None)`
- `featurelifted.cached` (function) `(cache, key=<function hashkey>, lock=None, condition=None, info=False)`
- `featurelifted.hashkey` (function) `(*args, **kwargs)`
- `featurelifted.typedkey` (function) `(*args, **kwargs)`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: LRU eviction order with touch-on-get and maxsize enforcement. Required observable cases include lru cache basic get set; lru eviction order; lru maxsize enforced.
- **B002**: The extracted feature must support this observable behavior: LFU frequency buckets and least-frequent eviction. Required observable cases include lfu evicts lowest frequency.
- **B003**: The extracted feature must support this observable behavior: TTL expiry with injectable timer and doubly-linked expiry list. Required observable cases include ttl expiry with mock timer.
- **B004**: The extracted feature must support this observable behavior: cached decorator memoization with optional cache_info hits/misses. Required observable cases include ttl cache stores value; cached decorator memoizes; cached info tracks hits and misses.
- **B005**: The extracted feature must support this observable behavior: hashkey and typedkey cache key functions for decorator kwargs and types. Required observable cases include ttl cache stores value; typedkey distinguishes value types.
- **B006**: The package exposes the required task API paths `featurelifted.LRUCache`, `featurelifted.LRUCache.maxsize`, `featurelifted.TTLCache`, `featurelifted.LFUCache`, `featurelifted.cached`, `featurelifted.hashkey`, `featurelifted.typedkey` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_lru_cache_basic_get_set`

- mapping: `B001`
- API: `featurelifted.LRUCache`
- risk: `state_mutation`
- A001 `assert` L10: `cache['a'] == 1`
- A002 `assert` L11: `cache['b'] == 2`
- A003 `assert` L12: `len(cache) == 2`

### `public_tests/test_public_api.py::test_ttl_cache_stores_value`

- mapping: `B004, B005`
- API: `featurelifted.TTLCache`
- risk: `state_mutation`
- A001 `assert` L18: `cache[1] == 'one'`
- A002 `assert` L19: `1 in cache`

### `public_tests/test_public_api.py::test_cached_decorator_memoizes`

- mapping: `B004`
- API: `featurelifted.LRUCache, featurelifted.cached`
- risk: `state_mutation`
- A001 `assert` L31: `add(2, 3) == 5`
- A002 `assert` L32: `add(2, 3) == 5`
- A003 `assert` L33: `calls == [(2, 3)]`

### `hidden_tests/test_hidden_behavior.py::test_lru_eviction_order`

- mapping: `B001`
- API: `featurelifted.LRUCache`
- risk: `ordering_semantics`
- A001 `assert` L27: `1 not in cache`
- A002 `assert` L28: `cache[2] == 'b'`
- A003 `assert` L29: `cache[3] == 'c'`
- A004 `assert` L33: `3 not in cache`
- A005 `assert` L34: `cache[2] == 'b'`
- A006 `assert` L35: `cache[4] == 'd'`

### `hidden_tests/test_hidden_behavior.py::test_lfu_evicts_lowest_frequency`

- mapping: `B002`
- API: `featurelifted.LFUCache`
- risk: `none`
- A001 `assert` L44: `1 in cache`
- A002 `assert` L45: `2 not in cache`
- A003 `assert` L46: `3 in cache`

### `hidden_tests/test_hidden_behavior.py::test_ttl_expiry_with_mock_timer`

- mapping: `B003`
- API: `featurelifted.TTLCache`
- risk: `exception_semantics`
- A001 `assert` L53: `cache['token'] == 'secret'`
- A002 `assert` L56: `'token' not in cache`
- A003 `raises` L57: `pytest.raises(KeyError)`

### `hidden_tests/test_hidden_behavior.py::test_lru_maxsize_enforced`

- mapping: `B001`
- API: `featurelifted.LRUCache`
- risk: `none`
- A001 `assert` L63: `cache.maxsize == 3`
- A002 `assert` L66: `len(cache) == 3`
- A003 `assert` L67: `0 not in cache`
- A004 `assert` L68: `1 not in cache`
- A005 `assert` L69: `2 not in cache`
- A006 `assert` L70: `3 in cache and 4 in cache and (5 in cache)`

### `hidden_tests/test_hidden_behavior.py::test_typedkey_distinguishes_value_types`

- mapping: `B005`
- API: `featurelifted.LRUCache, featurelifted.cached, featurelifted.typedkey`
- risk: `none`
- A001 `assert` L84: `len(calls) == 2`

### `hidden_tests/test_hidden_behavior.py::test_cached_info_tracks_hits_and_misses`

- mapping: `B004`
- API: `featurelifted.LRUCache, featurelifted.cached`
- risk: `state_mutation`
- A001 `assert` L94: `double(3) == 6`
- A002 `assert` L95: `double(3) == 6`
- A003 `assert` L97: `info.hits == 1`
- A004 `assert` L98: `info.misses == 1`

### `hidden_tests/test_hidden_behavior.py::test_no_cachetools_import_surface`

- mapping: `B007`
- API: `featurelifted.__file__`
- risk: `filesystem_resource, state_mutation`
- A001 `assert` L108: `not import_pattern.search(text)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.LFUCache, featurelifted.LRUCache, featurelifted.TTLCache, featurelifted.cached, featurelifted.hashkey, featurelifted.typedkey`
- risk: `none`
- A001 `assert` L14: `isinstance(LRUCache, type)`
- A002 `assert` L15: `LRUCache is not None`
- A003 `assert` L16: `isinstance(TTLCache, type)`
- A004 `assert` L17: `isinstance(LFUCache, type)`
- A005 `assert` L18: `callable(cached)`
- A006 `assert` L19: `callable(hashkey)`
- A007 `assert` L20: `callable(typedkey)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `cachetools`
- source entrypoints: `cachetools.LRUCache, cachetools.TTLCache, cachetools.LFUCache, cachetools.cached, cachetools.keys.hashkey, cachetools.keys.typedkey`
- oracle source files: `src/cachetools/__init__.py, src/cachetools/keys.py, src/cachetools/_cached.py`
- runtime dependencies: `none`
- oracle notes: Oracle copies cache eviction core modules; excludes async, func decorators, cachedmethod, benchmarks, and docs.
