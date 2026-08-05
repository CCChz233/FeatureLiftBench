# pytest__marker_registry_core__hard3_001

- release: `frozen_python150`
- lift: `Composite`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `5/12`

## Required API

- `featurelifted.MarkerRegistry` (class) `() -> 'None'`
- `featurelifted.MarkerRegistry.from_ini` (method) `(value: 'str | list[str]') -> "'MarkerRegistry'"`
- `featurelifted.MarkerRegistry.check_unknown` (method) `(self, name: 'str', *, strict: 'bool' = False) -> 'None'`
- `featurelifted.MarkerRegistry.get` (method) `(self, name: 'str') -> 'Marker | None'`
- `featurelifted.MarkerRegistry.merge_plugin_markers` (method) `(self, plugin_markers: 'dict[str, str]') -> 'None'`
- `featurelifted.MarkerRegistry.register` (method) `(self, name: 'str', description: 'str' = '', *, _overwrite: 'bool' = False) -> 'None'`
- `featurelifted.Marker` (class) `(name: 'str', description: 'str' = '', *, args: 'tuple' = (), kwargs: 'dict | None' = None) -> 'None'`
- `featurelifted.UnknownMarkerWarning` (exception)

## Public Behaviors

- **B001**: `MarkerRegistry.from_ini` parses marker lines from ini configuration.
- **B002**: `merge_plugin_markers` adds plugin-provided markers without overwriting existing ones.
- **B003**: `check_unknown` warns or raises for unregistered markers.
- **B004**: The package exposes the required task API paths `featurelifted.MarkerRegistry`, `featurelifted.MarkerRegistry.from_ini`, `featurelifted.MarkerRegistry.check_unknown`, `featurelifted.MarkerRegistry.get`, `featurelifted.MarkerRegistry.merge_plugin_markers`, `featurelifted.MarkerRegistry.register`, `featurelifted.Marker`, `featurelifted.UnknownMarkerWarning` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_from_ini_registers_markers`

- mapping: `B002, B003`
- API: `featurelifted.MarkerRegistry, featurelifted.MarkerRegistry.from_ini`
- risk: `none`
- A001 `assert` L7: `registry.get('slow').description == 'slow tests'`

### `hidden_tests/test_hidden_contract.py::test_merge_plugin_markers_does_not_overwrite`

- mapping: `B001, B002, B003`
- API: `featurelifted.MarkerRegistry`
- risk: `none`
- A001 `assert` L11: `registry.get('slow').description == 'original'`
- A002 `assert` L12: `registry.get('xfail').description == 'expected failure'`

### `hidden_tests/test_hidden_contract.py::test_check_unknown_warns`

- mapping: `B003`
- API: `featurelifted.MarkerRegistry, featurelifted.UnknownMarkerWarning`
- risk: `none`
- A001 `assert` L20: `any((isinstance(item.message, UnknownMarkerWarning) for item in caught))`

### `hidden_tests/test_hidden_contract.py::test_check_unknown_strict_raises`

- mapping: `B003`
- API: `featurelifted.MarkerRegistry`
- risk: `implicit_no_exception_assertion`
- assertion: implicit successful execution

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.Marker, featurelifted.MarkerRegistry, featurelifted.UnknownMarkerWarning`
- risk: `none`
- A001 `assert` L11: `isinstance(MarkerRegistry, type)`
- A002 `assert` L12: `hasattr(MarkerRegistry, 'from_ini')`
- A003 `assert` L13: `hasattr(MarkerRegistry, 'check_unknown')`
- A004 `assert` L14: `hasattr(MarkerRegistry, 'get')`
- A005 `assert` L15: `hasattr(MarkerRegistry, 'merge_plugin_markers')`
- A006 `assert` L16: `hasattr(MarkerRegistry, 'register')`
- A007 `assert` L17: `isinstance(Marker, type)`
- A008 `assert` L18: `issubclass(UnknownMarkerWarning, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `pytest, _pytest`
- source entrypoints: `_pytest.mark.structures.Mark`
- oracle source files: `repo/src/_pytest/mark/structures.py, repo/src/_pytest/config/__init__.py`
- runtime dependencies: `none`
- oracle notes: Marker registry subset without test collection.
