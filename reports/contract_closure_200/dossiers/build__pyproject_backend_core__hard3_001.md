# build__pyproject_backend_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `4/8`

## Required API

- `featurelifted.validate_source_directory` (function) `(source_dir: 'str') -> 'None'`
- `featurelifted.parse_build_system_table` (function) `(pyproject: 'dict[str, Any]') -> 'dict[str, Any]'`
- `featurelifted.BuildException` (exception)
- `featurelifted.BuildSystemTableValidationError` (exception)

## Public Behaviors

- **B001**: When parse_build_system_table receives pyproject data, it validates build-system.requires and build-backend and raises BuildSystemTableValidationError for malformed tables.
- **B002**: When validate_source_directory checks a source tree, it accepts valid project roots and raises BuildException for missing or invalid source directories.
- **B003**: The package exposes the required task API paths `featurelifted.validate_source_directory`, `featurelifted.parse_build_system_table`, `featurelifted.BuildException`, `featurelifted.BuildSystemTableValidationError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_default_build_system_when_missing`

- mapping: `B001`
- API: `featurelifted.parse_build_system_table`
- risk: `none`
- A001 `assert` L7: `table['build-backend'] == 'setuptools.build_meta'`
- A002 `assert` L8: `'setuptools' in table['requires'][0]`

### `hidden_tests/test_hidden_contract.py::test_unknown_build_system_property`

- mapping: `B001`
- API: `featurelifted.BuildSystemTableValidationError, featurelifted.parse_build_system_table`
- risk: `exact_error_text, exception_semantics`
- A001 `raises` L8: `pytest.raises(BuildSystemTableValidationError, match='Unknown properties')`

### `hidden_tests/test_hidden_contract.py::test_validate_source_directory_requires_project_file`

- mapping: `B002`
- API: `featurelifted.BuildException, featurelifted.validate_source_directory`
- risk: `exact_error_text, exception_semantics, filesystem_resource`
- A001 `raises` L15: `pytest.raises(BuildException, match='does not appear to be a Python project')`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B003`
- API: `featurelifted.BuildException, featurelifted.BuildSystemTableValidationError, featurelifted.parse_build_system_table, featurelifted.validate_source_directory`
- risk: `none`
- A001 `assert` L12: `callable(validate_source_directory)`
- A002 `assert` L13: `callable(parse_build_system_table)`
- A003 `assert` L14: `issubclass(BuildException, BaseException)`
- A004 `assert` L15: `issubclass(BuildSystemTableValidationError, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `build`
- source entrypoints: `build._builder.parse_build_system_table`
- oracle source files: `repo/src/build/_builder.py, repo/src/build/_exceptions.py`
- runtime dependencies: `none`
- oracle notes: Build-system table subset without isolated env runner.
