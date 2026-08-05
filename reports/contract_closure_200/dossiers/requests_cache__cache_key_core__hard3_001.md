# requests_cache__cache_key_core__hard3_001

- release: `frozen_python150`
- lift: `Composite`
- coupling: `unknown`
- strict validation: `FAIL`
- tests/assertions: `9/26`

## Required API

- `featurelifted.CachePolicy` (class) `(should_store: 'bool', expiration_seconds: 'int | None', reason: 'str' = '') -> None`
- `featurelifted.CachePolicy.from_headers` (method) `(headers: 'dict[str, Any] | None', default: 'int | None' = None, now: 'datetime | None' = None) -> "'CachePolicy'"`
- `featurelifted.create_key` (function) `(method: 'str', url: 'str', params=None, headers: 'dict[str, Any] | None' = None, body: 'Any' = None, ignored_parameters=None, match_headers: 'bool | list[str] | tuple[str, ...]' = False, verify: 'bool' = True, serializer: 'Any' = None, content_root_key: 'str | None' = None) -> 'str'`
- `featurelifted.get_expiration` (function) `(headers: 'dict[str, Any] | None', default: 'int | None' = None, now: 'datetime | None' = None) -> 'int | None'`
- `featurelifted.create_cache_key` (function) `(request: 'Any', **kwargs: 'Any') -> 'str'`
- `featurelifted.normalize_body` (function) `(body: 'Any', headers: 'dict[str, Any] | None' = None, ignored_parameters=None, content_root_key: 'str | None' = None) -> 'bytes'`
- `featurelifted.normalize_headers` (function) `(headers: 'dict[str, Any] | None', ignored_parameters=None) -> 'dict[str, str]'`
- `featurelifted.normalize_params` (function) `(value: 'Any', ignored_parameters=None) -> 'str'`

## Public Behaviors

- **B001**: create_key normalizes method, URL, parameters, selected headers, and body before returning a deterministic cache-key digest.
- **B002**: create_cache_key reads request-like objects and produces the same key as create_key with equivalent explicit fields.
- **B003**: normalize_url lowercases scheme and host, merges explicit parameters, sorts query items, and preserves key-only or repeated parameters.
- **B004**: normalize_params sorts parameters and redacts configured ignored values without removing their keys.
- **B005**: normalize_headers includes only matched headers, normalizes names and whitespace, and deterministically orders multi-value content.
- **B006**: normalize_body canonicalizes JSON key order and form-encoded parameters and redacts ignored values in both body forms.
- **B007**: get_matched_headers returns the normalized header subset requested by match_headers and excludes unmatched headers.
- **B008**: CachePolicy.from_headers interprets Cache-Control and Expires headers into storage and expiration decisions.
- **B009**: get_expiration returns max-age seconds, Expires relative to now, no-store suppression, or the declared default when no directive applies.
- **B010**: `Cache-Control: max-age=N` sets expiration to `N` seconds.
- **B011**: Use `default` expiration when no cache header applies.
- **B012**: The package exposes the required task API paths `featurelifted.CachePolicy`, `featurelifted.CachePolicy.from_headers`, `featurelifted.create_key`, `featurelifted.get_expiration`, `featurelifted.create_cache_key`, `featurelifted.normalize_body`, `featurelifted.normalize_headers`, `featurelifted.normalize_params` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_query_order_normalized`

- mapping: `B003, B004`
- API: `featurelifted.create_cache_key, featurelifted.create_key`
- risk: `ordering_semantics`
- A001 `assert` L12: `create_key('GET', 'https://example.test/items?b=2&a=1') == create_key('GET', 'https://example.test/items?a=1&b=2')`
- A002 `assert` L15: `create_cache_key(Request()) == create_key('GET', 'https://example.test/items?a=1&b=2', headers=Request.headers)`

### `public_tests/test_public_contract.py::test_ignored_parameter_redacts_value_for_matching`

- mapping: `B004`
- API: `featurelifted.create_key`
- risk: `none`
- A001 `assert` L23: `first == second`
- A002 `assert` L24: `first != different`

### `public_tests/test_public_contract.py::test_cache_control_max_age_and_no_store`

- mapping: `B010`
- API: `featurelifted.CachePolicy, featurelifted.CachePolicy.expiration_seconds, featurelifted.CachePolicy.from_headers`
- risk: `state_mutation`
- A001 `assert` L28: `CachePolicy.from_headers({'Cache-Control': 'max-age=60'}).expiration_seconds == 60`
- A002 `assert` L30: `policy.should_store is False`
- A003 `assert` L31: `policy.expiration_seconds is None`

### `hidden_tests/test_hidden_contract.py::test_json_body_sorting_and_redaction_affect_cache_key`

- mapping: `B001, B006`
- API: `featurelifted.create_key, featurelifted.normalize_body`
- risk: `state_mutation`
- A001 `assert` L23: `first == second`
- A002 `assert` L24: `normalize_body('{"b":2,"a":1}', headers=headers) == b'{"a":1,"b":2}'`

### `hidden_tests/test_hidden_contract.py::test_form_body_and_key_only_params_are_normalized`

- mapping: `B004, B006`
- API: `featurelifted.normalize_body, featurelifted.normalize_params`
- risk: `none`
- A001 `assert` L30: `normalize_params('b=2&a=1&flag') == 'a=1&b=2&flag'`
- A002 `assert` L31: `normalize_body('token=secret&b=2&a=1', headers=headers, ignored_parameters=['token']) == b'a=1&b=2&token=REDACTED'`

### `hidden_tests/test_hidden_contract.py::test_match_headers_controls_key_variation`

- mapping: `B002, B003, B005, B007, B008, B009, B010`
- API: `featurelifted.create_key`
- risk: `none`
- A001 `assert` L41: `create_key('GET', 'https://example.test', headers=base) == create_key('GET', 'https://example.test', headers=changed_accept)`
- A002 `assert` L44: `create_key('GET', 'https://example.test', headers=base, match_headers=['Accept']) == create_key('GET', 'https://example.test', headers=changed_trace, match_headers=['Accept'])`
- A003 `assert` L47: `create_key('GET', 'https://example.test', headers=base, match_headers=['Accept']) != create_key('GET', 'https://example.test', headers=changed_accept, match_headers=['Accept'])`

### `hidden_tests/test_hidden_contract.py::test_header_multi_value_normalization_and_redaction`

- mapping: `B005`
- API: `featurelifted.normalize_headers`
- risk: `none`
- A001 `assert` L55: `headers['accept'] == 'application/json, text/html'`
- A002 `assert` L56: `headers['authorization'] == 'REDACTED'`

### `hidden_tests/test_hidden_contract.py::test_expires_header_and_default_expiration`

- mapping: `B011`
- API: `featurelifted.CachePolicy, featurelifted.CachePolicy.expiration_seconds, featurelifted.CachePolicy.from_headers, featurelifted.get_expiration`
- risk: `none`
- A001 `assert` L62: `get_expiration({'Expires': 'Thu, 01 Jan 2026 00:01:30 GMT'}, now=now) == 90`
- A002 `assert` L63: `CachePolicy.from_headers({}, default=120).expiration_seconds == 120`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B012`
- API: `featurelifted.CachePolicy, featurelifted.create_cache_key, featurelifted.create_key, featurelifted.get_expiration, featurelifted.normalize_body, featurelifted.normalize_headers, featurelifted.normalize_params`
- risk: `none`
- A001 `assert` L15: `isinstance(CachePolicy, type)`
- A002 `assert` L16: `hasattr(CachePolicy, 'from_headers')`
- A003 `assert` L17: `callable(create_key)`
- A004 `assert` L18: `callable(get_expiration)`
- A005 `assert` L19: `callable(create_cache_key)`
- A006 `assert` L20: `callable(normalize_body)`
- A007 `assert` L21: `callable(normalize_headers)`
- A008 `assert` L22: `callable(normalize_params)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `requests_cache, requests, url_normalize`
- source entrypoints: `requests_cache.cache_keys.create_key, requests_cache.cache_keys.normalize_url, requests_cache.cache_keys.normalize_body, requests_cache.policy.expiration.get_expiration_datetime, requests_cache.policy.directives.CacheDirectives`
- oracle source files: `repo/requests_cache/cache_keys.py, repo/requests_cache/policy/expiration.py, repo/requests_cache/policy/directives.py, repo/requests_cache/_utils.py, repo/pyproject.toml, repo/LICENSE`
- runtime dependencies: `none`
- oracle notes: Task-scoped cache key and expiration policy extraction. HTTP sessions, storage backends, serializers, Redis/MongoDB/SQLite/filesystem cache layers, and network behavior are intentionally excluded.

## Machine Issues

- public_tests/test_public_contract.py uses undeclared API reference featurelifted.CachePolicy.expiration_seconds
- hidden_tests/test_hidden_contract.py uses undeclared API reference featurelifted.CachePolicy.expiration_seconds
