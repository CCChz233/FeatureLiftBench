# pytest__ini_markers_core__001

- release: `frozen_python150`
- lift: `Composite`
- coupling: `unknown`
- strict validation: `FAIL`
- tests/assertions: `6/13`

## Required API

- `featurelifted.MarkerRegistry` (class) `(lines: 'list[str]' = <factory>) -> None`
- `featurelifted.MarkerRegistry.from_ini` (method) `(value: 'str | list[str]') -> "'MarkerRegistry'"`
- `featurelifted.MarkerRegistry.names` (method) `(self) -> 'list[str]'`
- `featurelifted.parse_linelist` (function) `(value: 'str | list[str]') -> 'list[str]'`
- `featurelifted.split_marker_line` (function) `(line: 'str') -> 'tuple[str, str]'`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse multiline ini markers values into linelist entries. Required observable cases include parse multiline markers; split marker line whitespace.
- **B002**: The extracted feature must support this observable behavior: append marker lines preserving order. Required observable cases include append marker line; registry module order preserved.
- **B003**: The extracted feature must support this observable behavior: split marker lines into name and description (strip name; preserve description whitespace). Required observable cases include linelist strips blank lines; split marker line whitespace.
- **B004**: The extracted feature must support this observable behavior: strip whitespace from linelist entries. Required observable cases include linelist strips blank lines.
- **B005**: The extracted feature must support this observable behavior: MarkerRegistry preserves marker declaration order from ini lines. Required observable cases include append marker line; split marker line whitespace.
- **B006**: The package exposes the required task API paths `featurelifted.MarkerRegistry`, `featurelifted.MarkerRegistry.from_ini`, `featurelifted.MarkerRegistry.names`, `featurelifted.parse_linelist`, `featurelifted.split_marker_line` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_parse_multiline_markers`

- mapping: `B001`
- API: `featurelifted.MarkerRegistry, featurelifted.MarkerRegistry.from_lines, featurelifted.parse_linelist`
- risk: `none`
- A001 `assert` L12: `reg.names() == ['a1', 'a2']`
- A002 `assert` L13: `reg.description('a1') == 'web test'`

### `public_tests/test_public_api.py::test_append_marker_line`

- mapping: `B002, B005`
- API: `featurelifted.MarkerRegistry`
- risk: `none`
- A001 `assert` L20: `reg.description('slow') == 'slow tests'`
- A002 `assert` L21: `reg.description('fast') == ''`

### `hidden_tests/test_hidden_behavior.py::test_linelist_strips_blank_lines`

- mapping: `B003, B004`
- API: `featurelifted.parse_linelist`
- risk: `none`
- A001 `assert` L7: `parse_linelist('a\nb\n\n c ') == ['a', 'b', 'c']`

### `hidden_tests/test_hidden_behavior.py::test_split_marker_line_whitespace`

- mapping: `B001, B003, B005`
- API: `featurelifted.split_marker_line`
- risk: `none`
- A001 `assert` L12: `name == 'a1'`
- A002 `assert` L13: `desc == '  whitespace marker  '`

### `hidden_tests/test_hidden_behavior.py::test_registry_module_order_preserved`

- mapping: `B002`
- API: `featurelifted.MarkerRegistry, featurelifted.MarkerRegistry.from_ini`
- risk: `ordering_semantics`
- A001 `assert` L18: `reg.names() == ['z', 'a']`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.MarkerRegistry, featurelifted.parse_linelist, featurelifted.split_marker_line`
- risk: `none`
- A001 `assert` L11: `isinstance(MarkerRegistry, type)`
- A002 `assert` L12: `hasattr(MarkerRegistry, 'from_ini')`
- A003 `assert` L13: `hasattr(MarkerRegistry, 'names')`
- A004 `assert` L14: `callable(parse_linelist)`
- A005 `assert` L15: `callable(split_marker_line)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `pytest, _pytest`
- source entrypoints: `_pytest.config.Config.getini, _pytest.config.Config.addinivalue_line, _pytest.mark.__init__.pytest_addoption`
- oracle source files: `none`
- runtime dependencies: `none`
- oracle notes: Subset extracted into ini_markers module mirroring linelist + marker line parsing.

## Machine Issues

- public_tests/test_public_api.py uses undeclared API reference featurelifted.MarkerRegistry.from_lines
