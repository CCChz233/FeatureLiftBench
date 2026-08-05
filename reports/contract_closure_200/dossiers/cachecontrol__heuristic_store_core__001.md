# cachecontrol__heuristic_store_core__001

- release: `external50`
- lift: `Composite`
- coupling: `data_model_coupling`
- strict validation: `PASS`
- tests/assertions: `9/17`

## Required API

- `featurelifted.DictCache` (class)
- `featurelifted.DictCache.get` (method)
- `featurelifted.DictCache.set` (method)
- `featurelifted.DictCache.delete` (method)
- `featurelifted.BaseCache` (class)
- `featurelifted.ExpiresAfter` (class)
- `featurelifted.Serializer` (class)
- `featurelifted.CacheController` (class)
- `featurelifted.CacheController.cache` (attribute)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: DictCache get/set/delete. Required observable cases include dict cache roundtrip.
- **B002**: The extracted feature must support this observable behavior: ExpiresAfter and Serializer construction. Required observable cases include expires after construct; serializer construct; expires after days hours; serializer serde version.
- **B003**: The extracted feature must support this observable behavior: CacheController wraps a cache and DictCache subclasses BaseCache. Required observable cases include cache controller construct; base cache interface.
- **B004**: No live HTTP is required; tests use in-memory DictCache only.
- **B005**: The package exposes DictCache/BaseCache/ExpiresAfter/Serializer/CacheController with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: cachecontrol.

## Tests

### `public_tests/test_public_api.py::test_dict_cache_roundtrip`

- mapping: `B001`
- API: `featurelifted.DictCache`
- risk: `state_mutation`
- A001 `assert` L9: `cache.get('k') == b'value'`
- A002 `assert` L11: `cache.get('k') is None`

### `public_tests/test_public_api.py::test_expires_after_construct`

- mapping: `B002`
- API: `featurelifted.ExpiresAfter`
- risk: `none`
- A001 `assert` L16: `h is not None`

### `public_tests/test_public_api.py::test_serializer_construct`

- mapping: `B003`
- API: `featurelifted.Serializer`
- risk: `none`
- A001 `assert` L20: `Serializer() is not None`

### `hidden_tests/test_hidden_behavior.py::test_base_cache_interface`

- mapping: `B001`
- API: `featurelifted.BaseCache, featurelifted.DictCache`
- risk: `state_mutation`
- A001 `assert` L10: `issubclass(DictCache, BaseCache)`

### `hidden_tests/test_hidden_behavior.py::test_cache_controller_construct`

- mapping: `B002`
- API: `featurelifted.CacheController, featurelifted.DictCache`
- risk: `state_mutation`
- A001 `assert` L15: `ctrl.cache is not None`

### `hidden_tests/test_hidden_behavior.py::test_expires_after_days_hours`

- mapping: `B003`
- API: `featurelifted.ExpiresAfter`
- risk: `none`
- A001 `assert` L20: `getattr(h, 'delta', None) is not None or h is not None`

### `hidden_tests/test_hidden_behavior.py::test_serializer_serde_version`

- mapping: `B004`
- API: `featurelifted.Serializer`
- risk: `none`
- A001 `assert` L26: `version`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L35: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.DictCache, featurelifted.DictCache.delete, featurelifted.DictCache.get, featurelifted.DictCache.set`
- risk: `none`
- A001 `assert` L5: `hasattr(featurelifted, 'BaseCache')`
- A002 `assert` L6: `hasattr(featurelifted, 'CacheController')`
- A003 `assert` L7: `hasattr(featurelifted, 'DictCache')`
- A004 `assert` L8: `hasattr(featurelifted, 'ExpiresAfter')`
- A005 `assert` L9: `hasattr(featurelifted, 'Serializer')`
- A006 `assert` L10: `callable(featurelifted.DictCache.get)`
- A007 `assert` L11: `callable(featurelifted.DictCache.set)`
- A008 `assert` L12: `callable(featurelifted.DictCache.delete)`

## Dependency / Oracle Evidence

- allowed dependencies: `certifi, charset-normalizer, idna, msgpack, requests, urllib3`
- forbidden imports: `cachecontrol`
- source entrypoints: `none`
- oracle source files: `cachecontrol/cache.py, cachecontrol/heuristics.py, cachecontrol/serialize.py, cachecontrol/controller.py`
- runtime dependencies: `certifi, charset-normalizer, idna, msgpack, requests, urllib3`
- oracle notes: Offline DictCache + ExpiresAfter + Serializer; no live HTTP.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
