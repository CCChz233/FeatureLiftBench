# coverage__path_remap_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `7/12`

## Required API

- `featurelifted.PathAliases` (class) `(debugfn: 'Callable[[str], None] | None' = None, relative: 'bool' = False) -> 'None'`
- `featurelifted.PathAliases.map` (method) `(self, path: 'str', exists: 'Callable[[str], bool]' = <function source_exists>) -> 'str'`
- `featurelifted.PathAliases.add` (method) `(self, pattern: 'str', result: 'str') -> 'None'`
- `featurelifted.exceptions` (module)
- `featurelifted.exceptions.ConfigError` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: register glob-style path prefix aliases. Required observable cases include path aliases maps wildcard prefix; path aliases leaves unmatched paths; path aliases multiple rules; path aliases rejects trailing wildcards; path aliases skips nonexistent targets; path aliases relative pattern.
- **B002**: The extracted feature must support this observable behavior: map absolute and relative paths through the first matching alias. Required observable cases include path aliases maps wildcard prefix; path aliases leaves unmatched paths; path aliases multiple rules; path aliases relative pattern.
- **B003**: The extracted feature must support this observable behavior: normalize path separators to the alias result style. Required observable cases include path aliases skips nonexistent targets.
- **B004**: The extracted feature must support this observable behavior: reject alias patterns ending in wildcards with ConfigError (message: must not end with wildcards). Required observable cases include path aliases rejects trailing wildcards.
- **B005**: The extracted feature must support this observable behavior: skip mappings when the mapped target path does not exist. Required observable cases include path aliases skips nonexistent targets.
- **B006**: The package exposes the required task API paths `featurelifted.PathAliases`, `featurelifted.PathAliases.map`, `featurelifted.PathAliases.add`, `featurelifted.exceptions`, `featurelifted.exceptions.ConfigError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_path_aliases_maps_wildcard_prefix`

- mapping: `B001, B002`
- API: `featurelifted.PathAliases, featurelifted.exceptions`
- risk: `none`
- A001 `assert` L15: `mapped.replace('\\', '/').endswith('mysrc/a.py')`

### `public_tests/test_public_api.py::test_path_aliases_leaves_unmatched_paths`

- mapping: `B001, B002`
- API: `featurelifted.PathAliases, featurelifted.exceptions`
- risk: `none`
- A001 `assert` L22: `aliases.map(original, exists=lambda _path: True) == original`

### `hidden_tests/test_hidden_behavior.py::test_path_aliases_multiple_rules`

- mapping: `B001, B002`
- API: `featurelifted.PathAliases, featurelifted.exceptions`
- risk: `none`
- A001 `assert` L16: `aliases.map('/home/foo/src/a.py', exists=lambda _path: True).replace('\\', '/').endswith('mysrc/a.py')`
- A002 `assert` L19: `aliases.map('/lib/foo/libsrc/a.py', exists=lambda _path: True).replace('\\', '/').endswith('mylib/a.py')`

### `hidden_tests/test_hidden_behavior.py::test_path_aliases_rejects_trailing_wildcards`

- mapping: `B001, B004`
- API: `featurelifted.PathAliases, featurelifted.exceptions`
- risk: `exact_error_text, exception_semantics`
- A001 `raises` L27: `pytest.raises(ConfigError, match='must not end with wildcards')`

### `hidden_tests/test_hidden_behavior.py::test_path_aliases_skips_nonexistent_targets`

- mapping: `B001, B003, B005`
- API: `featurelifted.PathAliases, featurelifted.exceptions`
- risk: `none`
- A001 `assert` L35: `aliases.map(original, exists=lambda _path: False) == original`

### `hidden_tests/test_hidden_behavior.py::test_path_aliases_relative_pattern`

- mapping: `B001, B002`
- API: `featurelifted.PathAliases, featurelifted.exceptions`
- risk: `none`
- A001 `assert` L42: `mapped.replace('\\', '/') == 'src/proj/a.py'`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.PathAliases, featurelifted.exceptions`
- risk: `none`
- A001 `assert` L10: `isinstance(PathAliases, type)`
- A002 `assert` L11: `hasattr(PathAliases, 'map')`
- A003 `assert` L12: `hasattr(PathAliases, 'add')`
- A004 `assert` L13: `exceptions is not None`
- A005 `assert` L14: `issubclass(getattr(exceptions, 'ConfigError'), BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `coverage`
- source entrypoints: `coverage.files.PathAliases.add, coverage.files.PathAliases.map`
- oracle source files: `none`
- runtime dependencies: `none`
- oracle notes: PathAliases combine remap closure with glob conversion and canonical path helpers from files.py.
