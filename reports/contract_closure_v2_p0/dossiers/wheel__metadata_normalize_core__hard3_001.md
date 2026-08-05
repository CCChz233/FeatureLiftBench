# Contract V2 P0: wheel__metadata_normalize_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `5/15`

## Required API

- `featurelifted.safe_name` (function) `(name: 'str') -> 'str'`
- `featurelifted.safe_extra` (function) `(extra: 'str') -> 'str'`
- `featurelifted.split_sections` (function) `(text: 'str') -> 'list[tuple[str | None, list[str]]]'`
- `featurelifted.parse_wheel_filename` (function) `(filename: 'str') -> 'tuple[str, str, str]'`
- `featurelifted.urlsafe_b64encode` (function) `(data: 'bytes') -> 'bytes'`
- `featurelifted.WheelError` (exception)

## Public Behaviors

- **B001**: safe_name and safe_extra normalize project names and extras into their canonical metadata-safe forms.
- **B002**: parse_wheel_filename validates a wheel filename and returns the adapted three-tuple (normalized distribution, version, build tag or empty string); compatibility tags are validated but intentionally not returned.
- **B003**: split_sections preserves preamble and named section content in order, and urlsafe_b64encode returns unpadded URL-safe Base64 bytes.
- **B004**: The package exposes the required task API paths `featurelifted.safe_name`, `featurelifted.safe_extra`, `featurelifted.split_sections`, `featurelifted.parse_wheel_filename`, `featurelifted.urlsafe_b64encode`, `featurelifted.WheelError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_safe_name_and_extra`

- mapping: `B001`
- API: `featurelifted.safe_extra, featurelifted.safe_name`
- risk: `none`
- A001 `assert` L6: `safe_name('My Project') == 'My-Project'`
- A002 `assert` L7: `safe_extra('Dev Tools') == 'dev_tools'`

### `hidden_tests/test_hidden_contract.py::test_split_sections_and_b64`

- mapping: `B003`
- API: `featurelifted.split_sections, featurelifted.urlsafe_b64encode`
- risk: `none`
- A001 `assert` L15: `sections == [(None, ['readme']), ('metadata', ['name=demo']), ('files', ['README'])]`
- A002 `assert` L20: `urlsafe_b64encode(b'abc') == b'YWJj'`

### `hidden_tests/test_hidden_contract.py::test_parse_wheel_filename`

- mapping: `B002`
- API: `featurelifted.WheelError, featurelifted.parse_wheel_filename`
- risk: `exception_semantics`
- A001 `assert` L24: `parse_wheel_filename('my_pkg-1.0.0-py3-none-any.whl') == ('my-pkg', '1.0.0', '')`
- A002 `assert` L25: `parse_wheel_filename('my_pkg-1.0.0-2-py3-none-any.whl') == ('my-pkg', '1.0.0', '2')`
- A003 `raises` L26: `pytest.raises(WheelError)`

### `hidden_tests/test_hidden_contract.py::test_safe_name_extra_hidden`

- mapping: `B001`
- API: `featurelifted.safe_extra, featurelifted.safe_name`
- risk: `none`
- A001 `assert` L31: `safe_name('My Project.Plugin') == 'My-Project.Plugin'`
- A002 `assert` L32: `safe_extra('Dev Tools.Plugin') == 'dev_tools.plugin'`

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
- oracle notes: Explicit adapter over wheel metadata helpers: parse_wheel_filename returns distribution, version, and build only after validating the compatibility-tag suffix; split_sections and unpadded URL-safe Base64 behavior are included.
