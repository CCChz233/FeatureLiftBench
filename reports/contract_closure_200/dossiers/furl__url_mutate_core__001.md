# furl__url_mutate_core__001

- release: `external50`
- lift: `Adapted`
- coupling: `data_model_coupling`
- strict validation: `PASS`
- tests/assertions: `7/10`

## Required API

- `featurelifted.furl` (class) `(url: str = '')`
- `featurelifted.furl.url` (attribute)
- `featurelifted.furl.path` (attribute)
- `featurelifted.furl.args` (attribute)
- `featurelifted.furl.scheme` (attribute)
- `featurelifted.furl.host` (attribute)
- `featurelifted.furl.port` (attribute)
- `featurelifted.furl.fragment` (attribute)
- `featurelifted.Path` (class)
- `featurelifted.Path.segments` (attribute)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse and mutate path/query. Required observable cases include parse and mutate path; query args.
- **B002**: The extracted feature must support this observable behavior: scheme/host/port/fragment mutation. Required observable cases include set scheme host; fragment and port.
- **B003**: The extracted feature must support this observable behavior: remove query keys. Required observable cases include remove query key.
- **B004**: furl.url returns the serialized URL string.
- **B005**: The package exposes furl with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: furl.

## Tests

### `public_tests/test_public_api.py::test_parse_and_mutate_path`

- mapping: `B001`
- API: `featurelifted.furl`
- risk: `filesystem_resource, state_mutation`
- A001 `assert` L9: `'/a/b/c' in u.url`

### `public_tests/test_public_api.py::test_query_args`

- mapping: `B002`
- API: `featurelifted.furl`
- risk: `none`
- A001 `assert` L15: `'a=1' in u.url and 'b=2' in u.url`

### `public_tests/test_public_api.py::test_set_scheme_host`

- mapping: `B003`
- API: `featurelifted.furl`
- risk: `none`
- A001 `assert` L22: `u.url.startswith('https://new.test/')`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L13: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_hidden_behavior.py::test_fragment_and_port`

- mapping: `B001, B002, B004`
- API: `featurelifted.furl`
- risk: `none`
- A001 `assert` L23: `':9090/' in u.url`
- A002 `assert` L24: `'#updated' in u.url`

### `hidden_tests/test_hidden_behavior.py::test_remove_query_key`

- mapping: `B003`
- API: `featurelifted.furl`
- risk: `none`
- A001 `assert` L30: `'a=' not in u.url`
- A002 `assert` L31: `'b=2' in u.url`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `none detected`
- risk: `none`
- A001 `assert` L5: `hasattr(featurelifted, 'Path')`
- A002 `assert` L6: `hasattr(featurelifted, 'furl')`

## Dependency / Oracle Evidence

- allowed dependencies: `orderedmultidict, six`
- forbidden imports: `furl`
- source entrypoints: `none`
- oracle source files: `furl/furl.py`
- runtime dependencies: `orderedmultidict, six`
- oracle notes: Adapted furl URL/path/query mutation API.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
