# installer__wheel_record_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `5/8`

## Required API

- `featurelifted.parse_wheel_record` (function) `(content: 'str') -> 'list[tuple[str, str | None, int | None]]'`
- `featurelifted.find_dist_info` (function) `(names: 'list[str]') -> 'str | None'`
- `featurelifted.script_name` (function) `(entry_point: 'str') -> 'str'`

## Public Behaviors

- **B001**: `parse_wheel_record` parses CSV RECORD rows into `(path, digest, size)` tuples.
- **B002**: `find_dist_info` locates a unique `.dist-info` directory among archive names.
- **B003**: `script_name` derives console script names from entry point targets.
- **B004**: The package exposes the required task API paths `featurelifted.parse_wheel_record`, `featurelifted.find_dist_info`, `featurelifted.script_name` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_parse_wheel_record_row`

- mapping: `B001`
- API: `featurelifted.parse_wheel_record`
- risk: `none`
- A001 `assert` L7: `rows[0] == ('pkg/__init__.py', 'sha256=abc', 12)`

### `hidden_tests/test_hidden_contract.py::test_find_dist_info_unique`

- mapping: `B002`
- API: `featurelifted.find_dist_info`
- risk: `none`
- A001 `assert` L9: `find_dist_info(names) == 'demo-1.0.dist-info'`

### `hidden_tests/test_hidden_contract.py::test_multiple_dist_info_raises`

- mapping: `B002`
- API: `featurelifted.find_dist_info`
- risk: `exact_error_text, exception_semantics`
- A001 `raises` L14: `pytest.raises(ValueError, match='multiple')`

### `hidden_tests/test_hidden_contract.py::test_script_name_from_entry_point`

- mapping: `B001, B003`
- API: `featurelifted.script_name`
- risk: `none`
- A001 `assert` L19: `script_name('pkg.module:main') == 'main'`
- A002 `assert` L20: `script_name('pkg.module:Class.method') == 'Class'`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.find_dist_info, featurelifted.parse_wheel_record, featurelifted.script_name`
- risk: `none`
- A001 `assert` L11: `callable(parse_wheel_record)`
- A002 `assert` L12: `callable(find_dist_info)`
- A003 `assert` L13: `callable(script_name)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `installer`
- source entrypoints: `installer.records.parse_wheel_record`
- oracle source files: `repo/src/installer/records.py, repo/src/installer/_core.py`
- runtime dependencies: `none`
- oracle notes: Wheel RECORD planner without install destinations.
