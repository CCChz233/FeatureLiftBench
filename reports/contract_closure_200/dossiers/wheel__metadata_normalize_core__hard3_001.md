# wheel__metadata_normalize_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `4/15`

## Required API

- `featurelifted.safe_name` (function) `(name: 'str') -> 'str'`
- `featurelifted.safe_extra` (function) `(extra: 'str') -> 'str'`
- `featurelifted.split_sections` (function) `(text: 'str') -> 'list[tuple[str | None, list[str]]]'`
- `featurelifted.parse_wheel_filename` (function) `(filename: 'str') -> 'tuple[str, str, str]'`
- `featurelifted.urlsafe_b64encode` (function) `(data: 'bytes') -> 'bytes'`
- `featurelifted.WheelError` (exception)

## Public Behaviors

- **B001**: safe_name and safe_extra normalize project names and extras into their canonical metadata-safe forms.
- **B002**: parse_wheel_filename returns normalized distribution, version, build, and tag components and raises WheelError for invalid filenames.
- **B003**: split_sections separates metadata headers from named body sections without losing section content or order.
- **B004**: The package exposes the required task API paths `featurelifted.safe_name`, `featurelifted.safe_extra`, `featurelifted.split_sections`, `featurelifted.parse_wheel_filename`, `featurelifted.urlsafe_b64encode`, `featurelifted.WheelError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_safe_name_and_extra`

- mapping: `B001`
- API: `featurelifted.safe_extra, featurelifted.safe_name`
- risk: `none`
- A001 `assert` L6: `safe_name('My Project') == 'My-Project'`
- A002 `assert` L7: `safe_extra('Dev Tools') == 'dev_tools'`

### `hidden_tests/test_hidden_contract.py::test_split_sections_and_b64`

- mapping: `B001, B003`
- API: `featurelifted.split_sections, featurelifted.urlsafe_b64encode`
- risk: `none`
- A001 `assert` L9: `sections[0][0] is None`
- A002 `assert` L10: `sections[0][1] == ['readme']`
- A003 `assert` L11: `sections[1][0] == 'metadata'`
- A004 `assert` L12: `urlsafe_b64encode(b'abc') == b'YWJj'`

### `hidden_tests/test_hidden_contract.py::test_parse_wheel_filename`

- mapping: `B002`
- API: `featurelifted.WheelError, featurelifted.parse_wheel_filename`
- risk: `exception_semantics`
- A001 `assert` L17: `name == 'my-pkg'`
- A002 `assert` L18: `version == '1.0.0'`
- A003 `raises` L19: `pytest.raises(WheelError)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.WheelError, featurelifted.parse_wheel_filename, featurelifted.safe_extra, featurelifted.safe_name, featurelifted.split_sections, featurelifted.urlsafe_b64encode`
- risk: `none`
- A001 `assert` L14: `callable(safe_name)`
- A002 `assert` L15: `callable(safe_extra)`
- A003 `assert` L16: `callable(split_sections)`
- A004 `assert` L17: `callable(parse_wheel_filename)`
- A005 `assert` L18: `callable(urlsafe_b64encode)`
- A006 `assert` L19: `issubclass(WheelError, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `wheel`
- source entrypoints: `wheel._metadata.safe_name, wheel.wheelfile.WheelFile`
- oracle source files: `repo/src/wheel/_metadata.py, repo/src/wheel/wheelfile.py`
- runtime dependencies: `none`
- oracle notes: Metadata normalization subset without wheel packer.
