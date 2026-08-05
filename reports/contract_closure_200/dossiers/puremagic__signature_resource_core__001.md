# puremagic__signature_resource_core__001

- release: `external50`
- lift: `Direct`
- coupling: `resource_coupling`
- strict validation: `PASS`
- tests/assertions: `6/9`

## Required API

- `featurelifted.from_string` (function) `(string: str | bytes, mime: bool = False, filename=None) -> str`
- `featurelifted.from_stream` (function) `(stream, mime: bool = False, filename=None) -> str`
- `featurelifted.magic_string` (function) `(string, filename=None) -> list`
- `featurelifted.from_extension` (function) `(extension: str, mime: bool = True) -> str`
- `featurelifted.PureError` (exception)

## Public Behaviors

- **B001**: from_string and from_stream identify known byte signatures using bundled magic metadata.
- **B002**: MIME mode and from_extension return metadata associated with the selected signature or extension.
- **B003**: magic_string returns ranked match records and unknown or empty inputs raise documented errors.
- **B004**: The submitted package does not import puremagic or access external signature services.

## Tests

### `public_tests/test_public_api.py::test_string_and_stream_detection`

- mapping: `B001`
- API: `featurelifted.from_stream, featurelifted.from_string`
- risk: `none`
- A001 `assert` L8: `from_string(PNG) == '.png'`
- A002 `assert` L9: `from_stream(BytesIO(PNG)) == '.png'`

### `public_tests/test_public_api.py::test_mime_detection`

- mapping: `B002`
- API: `featurelifted.from_string`
- risk: `none`
- A001 `assert` L13: `from_string(PNG, mime=True) == 'image/png'`

### `hidden_tests/test_hidden_behavior.py::test_extension_metadata_lookup`

- mapping: `B002`
- API: `featurelifted.from_extension`
- risk: `none`
- A001 `assert` L6: `from_extension('.png') == 'image/png'`

### `hidden_tests/test_hidden_behavior.py::test_ranked_matches_and_unknown_input`

- mapping: `B001, B003`
- API: `featurelifted.PureError, featurelifted.magic_string`
- risk: `exception_semantics`
- A001 `assert` L11: `matches and matches[0].extension == '.pdf'`
- A002 `raises` L12: `pytest.raises((PureError, ValueError))`

### `hidden_tests/test_hidden_behavior.py::test_required_api_surface`

- mapping: `B003`
- API: `featurelifted.PureError, featurelifted.from_extension, featurelifted.from_stream, featurelifted.from_string, featurelifted.magic_string`
- risk: `none`
- A001 `assert` L17: `all((callable(x) for x in (from_string, from_stream, magic_string, from_extension)))`
- A002 `assert` L18: `issubclass(PureError, Exception)`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B004`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L27: `not pattern.search(path.read_text(encoding='utf-8'))`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `puremagic`
- source entrypoints: `none`
- oracle source files: `puremagic/main.py, puremagic/magic_data.json`
- runtime dependencies: `none`
- oracle notes: Balanced Python-200 replacement slot resource-direct-02; offline reference only.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
