# python_multipart__form_parse_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `14/47`

## Required API

- `featurelifted.Field` (class) `(name: 'bytes | None', *, content_type: 'str | None' = None) -> 'None'`
- `featurelifted.File` (class) `(file_name: 'bytes | None', field_name: 'bytes | None' = None, config: 'FileConfig' = {}, *, content_type: 'str | None' = None) -> 'None'`
- `featurelifted.FormParser` (class) `(content_type: 'str', on_field: 'Callable[[Field], None] | None', on_file: 'Callable[[File], None] | None', on_end: 'Callable[[], None] | None' = None, boundary: 'bytes | str | None' = None, file_name: 'bytes | None' = None, config: 'dict[Any, Any]' = {}) -> 'None'`
- `featurelifted.FormParser.write` (method) `(self, data: 'bytes') -> 'int'`
- `featurelifted.FormParser.finalize` (method) `(self) -> 'None'`
- `featurelifted.parse_form` (function) `(headers: 'dict[str, bytes]', input_stream: 'SupportsRead', on_field: 'Callable[[Field], None] | None', on_file: 'Callable[[File], None] | None', chunk_size: 'int' = 1048576) -> 'None'`
- `featurelifted.create_form_parser` (function) `(headers: 'dict[str, bytes]', on_field: 'Callable[[Field], None] | None', on_file: 'Callable[[File], None] | None', config: 'dict[Any, Any]' = {}) -> 'FormParser'`
- `featurelifted.parse_options_header` (function) `(value: 'str | bytes | None') -> 'tuple[bytes, dict[bytes, bytes]]'`
- `featurelifted.exceptions` (module)
- `featurelifted.exceptions.FormParserError` (exception)
- `featurelifted.exceptions.MultipartParseError` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: incremental multipart/form-data parsing via FormParser.write/finalize. Required observable cases include parse form helper; create form parser from headers; incremental chunked parsing.
- **B002**: The extracted feature must support this observable behavior: field and file parts with Content-Disposition, Content-Type, and filename. Required observable cases include parse simple text field; missing field name raises.
- **B003**: The extracted feature must support this observable behavior: parse_options_header boundary extraction from Content-Type. Required observable cases include parse simple text field; parse options header boundary; parse form helper; preamble before first boundary.
- **B004**: The extracted feature must support this observable behavior: base64 and quoted-printable Content-Transfer-Encoding. Required observable cases include base64 content transfer encoding.
- **B005**: The extracted feature must support this observable behavior: preamble before first boundary and epilogue after closing boundary. Required observable cases include preamble before first boundary; epilogue after closing boundary.
- **B006**: The extracted feature must support this observable behavior: MAX_MEMORY_FILE_SIZE spill to disk and configurable upload directory. Required observable cases include parse file upload metadata; max memory file size spills to disk; max header size exceeded.
- **B007**: The extracted feature must support this observable behavior: MAX_HEADER_COUNT and MAX_HEADER_SIZE enforcement. Required observable cases include max header size exceeded.
- **B008**: The package exposes the required task API paths `featurelifted.Field`, `featurelifted.File`, `featurelifted.FormParser`, `featurelifted.FormParser.write`, `featurelifted.FormParser.finalize`, `featurelifted.parse_form`, `featurelifted.create_form_parser`, `featurelifted.parse_options_header`, `featurelifted.exceptions`, `featurelifted.exceptions.FormParserError`, `featurelifted.exceptions.MultipartParseError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_parse_simple_text_field`

- mapping: `B002, B003`
- API: `none detected`
- risk: `none`
- A001 `assert` L32: `files == []`
- A002 `assert` L33: `len(fields) == 1`
- A003 `assert` L34: `fields[0].field_name == b'username'`
- A004 `assert` L35: `fields[0].value == b'alice'`

### `public_tests/test_public_api.py::test_parse_file_upload_metadata`

- mapping: `B006`
- API: `none detected`
- risk: `none`
- A001 `assert` L48: `fields == []`
- A002 `assert` L49: `len(files) == 1`
- A003 `assert` L51: `uploaded.field_name == b'upload'`
- A004 `assert` L52: `uploaded.file_name == b'note.txt'`
- A005 `assert` L53: `uploaded.content_type == 'text/plain'`
- A006 `assert` L55: `uploaded.file_object.read() == b'hello file'`

### `public_tests/test_public_api.py::test_parse_options_header_boundary`

- mapping: `B003`
- API: `featurelifted.parse_options_header`
- risk: `none`
- A001 `assert` L60: `ctype == b'multipart/form-data'`
- A002 `assert` L61: `params[b'boundary'] == b'----abc'`

### `public_tests/test_public_api.py::test_parse_form_helper`

- mapping: `B001, B003`
- API: `featurelifted.Field, featurelifted.File, featurelifted.parse_form`
- risk: `none`
- A001 `assert` L78: `len(fields) == 1`
- A002 `assert` L79: `fields[0].value == b'v'`
- A003 `assert` L80: `files == []`

### `public_tests/test_public_api.py::test_create_form_parser_from_headers`

- mapping: `B001`
- API: `featurelifted.Field, featurelifted.create_form_parser`
- risk: `none`
- A001 `assert` L95: `fields[0].field_name == b'a'`

### `hidden_tests/test_hidden_behavior.py::test_incremental_chunked_parsing`

- mapping: `B001`
- API: `featurelifted.Field, featurelifted.File, featurelifted.FormParser, featurelifted.exceptions`
- risk: `none`
- A001 `assert` L43: `len(fields) == 1`
- A002 `assert` L44: `fields[0].value == b'partial'`
- A003 `assert` L45: `files == []`

### `hidden_tests/test_hidden_behavior.py::test_base64_content_transfer_encoding`

- mapping: `B004`
- API: `featurelifted.exceptions`
- risk: `none`
- A001 `assert` L59: `fields == []`
- A002 `assert` L60: `len(files) == 1`
- A003 `assert` L62: `files[0].file_object.read() == b'Test'`

### `hidden_tests/test_hidden_behavior.py::test_preamble_before_first_boundary`

- mapping: `B003, B005`
- API: `featurelifted.exceptions`
- risk: `none`
- A001 `assert` L76: `fields == []`
- A002 `assert` L77: `len(files) == 1`
- A003 `assert` L79: `files[0].file_object.read() == b'payload'`

### `hidden_tests/test_hidden_behavior.py::test_epilogue_after_closing_boundary`

- mapping: `B005`
- API: `featurelifted.exceptions`
- risk: `none`
- A001 `assert` L92: `len(files) == 1`
- A002 `assert` L94: `files[0].file_object.read() == b'hello'`

### `hidden_tests/test_hidden_behavior.py::test_missing_field_name_raises`

- mapping: `B002`
- API: `featurelifted.exceptions`
- risk: `exact_error_text, exception_semantics`
- A001 `raises` L106: `pytest.raises(FormParserError, match='Field name not found')`

### `hidden_tests/test_hidden_behavior.py::test_max_memory_file_size_spills_to_disk`

- mapping: `B006`
- API: `featurelifted.exceptions`
- risk: `filesystem_resource`
- A001 `assert` L128: `fields == []`
- A002 `assert` L129: `len(files) == 1`
- A003 `assert` L131: `uploaded.in_memory is False`
- A004 `assert` L132: `uploaded.actual_file_name is not None`
- A005 `assert` L135: `os.path.exists(path)`
- A006 `assert` L137: `fh.read() == b'0123456789'`

### `hidden_tests/test_hidden_behavior.py::test_max_header_size_exceeded`

- mapping: `B006, B007`
- API: `featurelifted.exceptions`
- risk: `exact_error_text, exception_semantics`
- A001 `raises` L154: `pytest.raises(MultipartParseError, match='Maximum header size exceeded')`

### `hidden_tests/test_hidden_behavior.py::test_no_python_multipart_import_surface`

- mapping: `B009`
- API: `featurelifted.__file__, featurelifted.exceptions`
- risk: `filesystem_resource`
- A001 `assert` L164: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B008`
- API: `featurelifted.Field, featurelifted.File, featurelifted.FormParser, featurelifted.create_form_parser, featurelifted.exceptions, featurelifted.parse_form, featurelifted.parse_options_header`
- risk: `none`
- A001 `assert` L15: `isinstance(Field, type)`
- A002 `assert` L16: `isinstance(File, type)`
- A003 `assert` L17: `isinstance(FormParser, type)`
- A004 `assert` L18: `hasattr(FormParser, 'write')`
- A005 `assert` L19: `hasattr(FormParser, 'finalize')`
- A006 `assert` L20: `callable(parse_form)`
- A007 `assert` L21: `callable(create_form_parser)`
- A008 `assert` L22: `callable(parse_options_header)`
- A009 `assert` L23: `exceptions is not None`
- A010 `assert` L24: `issubclass(getattr(exceptions, 'FormParserError'), BaseException)`
- A011 `assert` L25: `issubclass(getattr(exceptions, 'MultipartParseError'), BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `python_multipart, multipart`
- source entrypoints: `python_multipart.multipart.FormParser, python_multipart.multipart.MultipartParser, python_multipart.multipart.Field, python_multipart.multipart.File, python_multipart.multipart.parse_form, python_multipart.multipart.create_form_parser, python_multipart.multipart.parse_options_header, python_multipart.decoders.Base64Decoder, python_multipart.decoders.QuotedPrintableDecoder`
- oracle source files: `python_multipart/__init__.py, python_multipart/multipart.py, python_multipart/decoders.py, python_multipart/exceptions.py`
- runtime dependencies: `none`
- oracle notes: Oracle splits multipart.py into constants, headers, models, base, multipart_parse, and form modules; omits urlencoded/octet-stream parsers and ASGI integration.
