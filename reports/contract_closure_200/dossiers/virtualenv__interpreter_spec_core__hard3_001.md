# virtualenv__interpreter_spec_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `5/11`

## Required API

- `featurelifted.parse_spec` (function) `(spec: 'str') -> 'tuple[str | None, tuple[str, ...]]'`
- `featurelifted.match_version` (function) `(version: 'str', constraint: 'str | None') -> 'bool'`
- `featurelifted.discover_paths` (function) `(candidates: 'list[str]', spec: 'str') -> 'list[str]'`
- `featurelifted.InvalidInterpreterSpec` (exception)

## Public Behaviors

- **B001**: `parse_spec` parses version constraints and path globs from interpreter specs.
- **B002**: `match_version` evaluates constraint operators including `~=`.
- **B003**: `discover_paths` filters candidate paths by spec.
- **B004**: The package exposes the required task API paths `featurelifted.parse_spec`, `featurelifted.match_version`, `featurelifted.discover_paths`, `featurelifted.InvalidInterpreterSpec` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_discover_paths_by_glob`

- mapping: `B003`
- API: `featurelifted.discover_paths, featurelifted.parse_spec`
- risk: `none`
- A001 `assert` L7: `constraint is None`
- A002 `assert` L9: `candidates == ['/usr/bin/python3.11']`

### `hidden_tests/test_hidden_contract.py::test_match_version_operators`

- mapping: `B002`
- API: `featurelifted.match_version`
- risk: `none`
- A001 `assert` L8: `match_version('3.11.2', '>=3.11')`
- A002 `assert` L9: `not match_version('3.10.0', '>=3.11')`
- A003 `assert` L10: `match_version('3.11.1', '~=3.11.0')`

### `hidden_tests/test_hidden_contract.py::test_version_constraint_filters_candidates`

- mapping: `B002, B003`
- API: `featurelifted.discover_paths`
- risk: `none`
- A001 `assert` L18: `candidates == ['/opt/python3.11/bin/python3.11']`

### `hidden_tests/test_hidden_contract.py::test_invalid_spec_raises`

- mapping: `B001`
- API: `featurelifted.InvalidInterpreterSpec, featurelifted.parse_spec`
- risk: `exception_semantics`
- A001 `raises` L22: `pytest.raises(InvalidInterpreterSpec)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.InvalidInterpreterSpec, featurelifted.discover_paths, featurelifted.match_version, featurelifted.parse_spec`
- risk: `none`
- A001 `assert` L12: `callable(parse_spec)`
- A002 `assert` L13: `callable(match_version)`
- A003 `assert` L14: `callable(discover_paths)`
- A004 `assert` L15: `issubclass(InvalidInterpreterSpec, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `virtualenv`
- source entrypoints: `virtualenv.discovery.py_info.parse_spec`
- oracle source files: `repo/src/virtualenv/discovery/py_info.py, repo/src/virtualenv/discovery/discover.py`
- runtime dependencies: `none`
- oracle notes: Interpreter spec parser without environment creation.
