# pathvalidate__sanitize_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `10/31`

## Required API

- `featurelifted.Platform` (class) `(*values)`
- `featurelifted.sanitize_filename` (function) `(filename: ~PathType, replacement_text: str = '', platform: Optional[~PlatformType] = None, max_len: Optional[int] = 255, fs_encoding: Optional[str] = None, check_reserved: Optional[bool] = None, null_value_handler: Optional[Callable[[ValidationError], str]] = None, reserved_name_handler: Optional[Callable[[ValidationError], str]] = None, additional_reserved_names: Optional[collections.abc.Sequence[str]] = None, validate_after_sanitize: bool = False) -> ~PathType`
- `featurelifted.sanitize_filepath` (function) `(file_path: ~PathType, replacement_text: str = '', platform: Optional[~PlatformType] = None, max_len: Optional[int] = None, fs_encoding: Optional[str] = None, check_reserved: Optional[bool] = None, null_value_handler: Optional[Callable[[ValidationError], str]] = None, reserved_name_handler: Optional[Callable[[ValidationError], str]] = None, additional_reserved_names: Optional[collections.abc.Sequence[str]] = None, normalize: bool = True, validate_after_sanitize: bool = False) -> ~PathType`
- `featurelifted.validate_filename` (function) `(filename: ~PathType, platform: Optional[~PlatformType] = None, min_len: int = 1, max_len: int = 255, fs_encoding: Optional[str] = None, check_reserved: bool = True, additional_reserved_names: Optional[collections.abc.Sequence[str]] = None) -> None`
- `featurelifted.validate_filepath` (function) `(file_path: ~PathType, platform: Optional[~PlatformType] = None, min_len: int = 1, max_len: Optional[int] = None, fs_encoding: Optional[str] = None, check_reserved: bool = True, additional_reserved_names: Optional[collections.abc.Sequence[str]] = None) -> None`
- `featurelifted.is_valid_filename` (function) `(filename: ~PathType, platform: Optional[~PlatformType] = None, min_len: int = 1, max_len: Optional[int] = None, fs_encoding: Optional[str] = None, check_reserved: bool = True, additional_reserved_names: Optional[collections.abc.Sequence[str]] = None) -> bool`
- `featurelifted.is_valid_filepath` (function) `(file_path: ~PathType, platform: Optional[~PlatformType] = None, min_len: int = 1, max_len: Optional[int] = None, fs_encoding: Optional[str] = None, check_reserved: bool = True, additional_reserved_names: Optional[collections.abc.Sequence[str]] = None) -> bool`
- `featurelifted.ValidationError` (exception)
- `featurelifted.ErrorReason` (class) `(*values)`
- `featurelifted.ErrorReason.INVALID_CHARACTER` (attribute)
- `featurelifted.ErrorReason.RESERVED_NAME` (attribute)
- `featurelifted.ReservedNameError` (exception)
- `featurelifted.InvalidCharError` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: sanitize_filename replaces invalid characters. Required observable cases include sanitize filename replaces invalid chars; validate filename accepts simple name; invalid character error reason.
- **B002**: The extracted feature must support this observable behavior: sanitize_filepath sanitizes each path segment. Required observable cases include sanitize filepath joins segments; sanitize filepath reserved segment.
- **B003**: The extracted feature must support this observable behavior: Windows reserved device names (CON, PRN, etc.) rejected or rewritten. Required observable cases include windows reserved name sanitize; windows reserved name validate raises.
- **B004**: The extracted feature must support this observable behavior: ValidationError exposes ErrorReason and reserved_name metadata. Required observable cases include filepath reserved name metadata.
- **B005**: The extracted feature must support this observable behavior: platform parameter selects Windows/Linux/macOS/universal rules. Required observable cases include windows reserved name validate raises.
- **B006**: The package exposes the required task API paths `featurelifted.Platform`, `featurelifted.sanitize_filename`, `featurelifted.sanitize_filepath`, `featurelifted.validate_filename`, `featurelifted.validate_filepath`, `featurelifted.is_valid_filename`, `featurelifted.is_valid_filepath`, `featurelifted.ValidationError`, `featurelifted.ErrorReason`, `featurelifted.ErrorReason.INVALID_CHARACTER`, `featurelifted.ErrorReason.RESERVED_NAME`, `featurelifted.ReservedNameError`, and 1 listed members with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_sanitize_filename_replaces_invalid_chars`

- mapping: `B001`
- API: `featurelifted.is_valid_filename, featurelifted.sanitize_filename, featurelifted.validate_filename`
- risk: `none`
- A001 `assert` L14: `sanitize_filename('foo:bar', replacement_text='_') == 'foo_bar'`
- A002 `assert` L16: `is_valid_filename('foo_bar')`

### `public_tests/test_public_api.py::test_sanitize_filepath_joins_segments`

- mapping: `B002`
- API: `featurelifted.is_valid_filepath, featurelifted.sanitize_filepath, featurelifted.validate_filepath`
- risk: `filesystem_resource`
- A001 `assert` L21: `sanitized == 'dir/sub-name/file.txt'`
- A002 `assert` L23: `is_valid_filepath(sanitized)`

### `public_tests/test_public_api.py::test_validate_filename_accepts_simple_name`

- mapping: `B001`
- API: `featurelifted.is_valid_filename, featurelifted.validate_filename`
- risk: `none`
- A001 `assert` L28: `is_valid_filename('report.csv')`

### `hidden_tests/test_hidden_behavior.py::test_windows_reserved_name_sanitize`

- mapping: `B003`
- API: `featurelifted.is_valid_filename, featurelifted.sanitize_filename`
- risk: `none`
- A001 `assert` L21: `sanitize_filename('CON', platform='windows') == 'CON_'`
- A002 `assert` L22: `is_valid_filename('CON_', platform='windows')`

### `hidden_tests/test_hidden_behavior.py::test_windows_reserved_name_validate_raises`

- mapping: `B003, B005`
- API: `featurelifted.ErrorReason, featurelifted.ErrorReason.RESERVED_NAME, featurelifted.ReservedNameError, featurelifted.validate_filename`
- risk: `exception_semantics`
- A001 `raises` L26: `pytest.raises(ReservedNameError)`
- A002 `assert` L28: `exc.value.reason == ErrorReason.RESERVED_NAME`
- A003 `assert` L29: `exc.value.reserved_name == 'CON'`

### `hidden_tests/test_hidden_behavior.py::test_sanitize_filepath_reserved_segment`

- mapping: `B002`
- API: `featurelifted.sanitize_filepath, featurelifted.validate_filepath`
- risk: `filesystem_resource`
- A001 `assert` L33: `sanitize_filepath('abc/CON/xyz', platform='universal') == 'abc/CON_/xyz'`

### `hidden_tests/test_hidden_behavior.py::test_invalid_character_error_reason`

- mapping: `B001`
- API: `featurelifted.ErrorReason, featurelifted.ErrorReason.INVALID_CHARACTER, featurelifted.ValidationError, featurelifted.is_valid_filename, featurelifted.validate_filename`
- risk: `exception_semantics`
- A001 `raises` L38: `pytest.raises(ValidationError)`
- A002 `assert` L40: `exc.value.reason == ErrorReason.INVALID_CHARACTER`
- A003 `assert` L41: `not is_valid_filename('a<b', platform='universal')`

### `hidden_tests/test_hidden_behavior.py::test_filepath_reserved_name_metadata`

- mapping: `B004`
- API: `featurelifted.ErrorReason, featurelifted.ErrorReason.RESERVED_NAME, featurelifted.ValidationError, featurelifted.validate_filepath`
- risk: `exception_semantics, filesystem_resource`
- A001 `raises` L45: `pytest.raises(ValidationError)`
- A002 `assert` L47: `exc.value.reason == ErrorReason.RESERVED_NAME`
- A003 `assert` L48: `exc.value.reserved_name == 'PRN'`

### `hidden_tests/test_hidden_behavior.py::test_no_pathvalidate_import_surface`

- mapping: `B007`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L58: `not import_pattern.search(text)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.ErrorReason, featurelifted.InvalidCharError, featurelifted.Platform, featurelifted.ReservedNameError, featurelifted.ValidationError, featurelifted.is_valid_filename, featurelifted.is_valid_filepath, featurelifted.sanitize_filename, featurelifted.sanitize_filepath, featurelifted.validate_filename, featurelifted.validate_filepath`
- risk: `none`
- A001 `assert` L19: `isinstance(Platform, type)`
- A002 `assert` L20: `callable(sanitize_filename)`
- A003 `assert` L21: `callable(sanitize_filepath)`
- A004 `assert` L22: `callable(validate_filename)`
- A005 `assert` L23: `callable(validate_filepath)`
- A006 `assert` L24: `callable(is_valid_filename)`
- A007 `assert` L25: `callable(is_valid_filepath)`
- A008 `assert` L26: `issubclass(ValidationError, BaseException)`
- A009 `assert` L27: `isinstance(ErrorReason, type)`
- A010 `assert` L28: `ErrorReason is not None`
- A011 `assert` L29: `ErrorReason is not None`
- A012 `assert` L30: `issubclass(ReservedNameError, BaseException)`
- A013 `assert` L31: `issubclass(InvalidCharError, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `pathvalidate`
- source entrypoints: `pathvalidate.sanitize_filename, pathvalidate.sanitize_filepath, pathvalidate.validate_filename, pathvalidate.validate_filepath, pathvalidate.is_valid_filename, pathvalidate.is_valid_filepath, pathvalidate.Platform, pathvalidate.error.ValidationError, pathvalidate.error.ErrorReason, pathvalidate.error.ReservedNameError, pathvalidate._filename.FileNameSanitizer, pathvalidate._filepath.FilePathSanitizer`
- oracle source files: `pathvalidate/__version__.py, pathvalidate/error.py, pathvalidate/handler.py, pathvalidate/_base.py, pathvalidate/_common.py, pathvalidate/_const.py, pathvalidate/_types.py, pathvalidate/_filename.py, pathvalidate/_filepath.py`
- runtime dependencies: `none`
- oracle notes: Oracle copies filename/filepath sanitization core; excludes click/argparse CLI, LTSV, and symbol helpers.
