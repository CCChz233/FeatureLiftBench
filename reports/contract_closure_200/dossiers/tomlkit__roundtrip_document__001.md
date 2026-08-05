# tomlkit__roundtrip_document__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `9/51`

## Required API

- `featurelifted.parse` (function) `(string: 'str | bytes') -> 'TOMLDocument'`
- `featurelifted.loads` (function) `(string: 'str | bytes') -> 'TOMLDocument'`
- `featurelifted.dumps` (function) `(data: 'Mapping[str, Any]', sort_keys: 'bool' = False) -> 'str'`
- `featurelifted.document` (function) `() -> 'TOMLDocument'`
- `featurelifted.table` (function) `(is_super_table: 'bool | None' = None) -> 'Table'`
- `featurelifted.inline_table` (function) `() -> 'InlineTable'`
- `featurelifted.array` (function) `(raw: 'str' = '[]') -> 'Array'`
- `featurelifted.aot` (function) `() -> 'AoT'`
- `featurelifted.string` (function) `(raw: 'str', *, literal: 'bool' = False, multiline: 'bool' = False, escape: 'bool' = True) -> 'String'`
- `featurelifted.item` (function) `(value: 'Any', _parent: 'Item | None' = None, _sort_keys: 'bool' = False) -> 'Item'`
- `featurelifted.exceptions` (module)
- `featurelifted.exceptions.InvalidUnicodeValueError` (exception)
- `featurelifted.exceptions.ParseError` (exception)
- `featurelifted.exceptions.UnexpectedCharError` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse TOML strings and bytes into mutable TOMLDocument objects. Required observable cases include string constructor and sorted dump preserve expected format.
- **B002**: The extracted feature must support this observable behavior: preserve comments, blank lines, table order, inline tables, literal strings, multiline strings, and array formatting when dumping parsed documents. Required observable cases include parse document values and roundtrip layout; editing preserves table order and comments; inline table array and parse errors; multiline literal strings and trailing comma arrays roundtrip.
- **B003**: The extracted feature must support this observable behavior: dump plain mappings, nested mappings, arrays, inline tables, and arrays of tables. Required observable cases include dump plain mappings and build document; arrays of tables and inline tables dump correctly.
- **B004**: The extracted feature must support this observable behavior: support document/table/inline_table/array/aot/string/item constructors. Required observable cases include inline table array and parse errors; arrays of tables and inline tables dump correctly; string constructor and sorted dump preserve expected format.
- **B005**: The extracted feature must support this observable behavior: support sorted-key dumping for mappings and parsed documents. Required observable cases include parse document values and roundtrip layout; dump plain mappings and build document; string constructor and sorted dump preserve expected format.
- **B006**: The extracted feature must support this observable behavior: support datetime, date, time, integers, floats, booleans, arrays, tables, dotted keys, and unicode strings. Required observable cases include dotted keys table redefinition and unicode errors.
- **B007**: The extracted feature must support this observable behavior: raise stable ParseError subclasses with line and column information for malformed TOML. Required observable cases include string constructor and sorted dump preserve expected format.
- **B008**: The package exposes the required task API paths `featurelifted.parse`, `featurelifted.loads`, `featurelifted.dumps`, `featurelifted.document`, `featurelifted.table`, `featurelifted.inline_table`, `featurelifted.array`, `featurelifted.aot`, `featurelifted.string`, `featurelifted.item`, `featurelifted.exceptions`, `featurelifted.exceptions.InvalidUnicodeValueError`, and 2 listed members with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_parse_document_values_and_roundtrip_layout`

- mapping: `B002, B005`
- API: `featurelifted.dumps, featurelifted.exceptions, featurelifted.parse`
- risk: `none`
- A001 `assert` L41: `doc['name'] == 'featurelift'`
- A002 `assert` L42: `doc['enabled'] is True`
- A003 `assert` L43: `doc['ports'] == [8000, 8001, 8002]`
- A004 `assert` L44: `doc['owner']['name'] == 'Ada'`
- A005 `assert` L45: `doc['owner']['dob'] == datetime(1979, 5, 27, 7, 32, tzinfo=timezone.utc)`
- A006 `assert` L46: `doc['database']['connection_max'] == 5000`
- A007 `assert` L47: `doc.as_string() == content`
- A008 `assert` L48: `dumps(doc) == content`

### `public_tests/test_public_api.py::test_editing_preserves_table_order_and_comments`

- mapping: `B002`
- API: `featurelifted.exceptions, featurelifted.parse`
- risk: `ordering_semantics`
- A001 `assert` L69: `doc.as_string() == dedent('        [tool.poetry]\n        name = "featurelift"\n\n        [bar]\n        name = "baz"\n\n        [tool.poetry.dependencies]\n        python = "^3.11"\n        pytest = "^8"\n        ')`

### `public_tests/test_public_api.py::test_dump_plain_mappings_and_build_document`

- mapping: `B003, B005`
- API: `featurelifted.document, featurelifted.dumps, featurelifted.exceptions`
- risk: `none`
- A001 `assert` L85: `dumps({'project': {'name': 'demo', 'classifiers': ['A', 'B']}}) == dedent('        [project]\n        name = "demo"\n        classifiers = ["A", "B"]\n        ')`
- A002 `assert` L92: `dumps({'zzz': 1, 'aaa': 'foo'}, sort_keys=True) == 'aaa = "foo"\nzzz = 1\n'`
- A003 `assert` L98: `dumps(doc) == dedent('        title = "Demo"\n\n        [owner]\n        name = "Ada"\n        active = true\n        ')`

### `public_tests/test_public_api.py::test_inline_table_array_and_parse_errors`

- mapping: `B002, B004`
- API: `featurelifted.aot, featurelifted.array, featurelifted.exceptions, featurelifted.inline_table, featurelifted.item, featurelifted.parse, featurelifted.string`
- risk: `exception_semantics`
- A001 `assert` L112: `table.as_string() == '{version = "1.0", optional = true}'`
- A002 `assert` L116: `values.as_string() == '[1, 2, 3]'`
- A003 `assert` L120: `item({'dependency': dependencies}).as_string() == dedent('        [[dependency]]\n        name = "requests"\n        ')`
- A004 `assert` L127: `string('hello "world"').as_string() == '"hello \\"world\\""'`
- A005 `assert` L128: `string('C:\\Users\\Ada', literal=True).as_string() == "'C:\\Users\\Ada'"`
- A006 `raises` L130: `pytest.raises(UnexpectedCharError)`
- A007 `assert` L133: `isinstance(excinfo.value, ParseError)`
- A008 `assert` L134: `excinfo.value.line == 1`
- A009 `assert` L135: `excinfo.value.col == 5`

### `hidden_tests/test_hidden_behavior.py::test_multiline_literal_strings_and_trailing_comma_arrays_roundtrip`

- mapping: `B002`
- API: `featurelifted.exceptions, featurelifted.parse`
- risk: `none`
- A001 `assert` L27: `doc['numbers'] == [1, 2]`
- A002 `assert` L28: `doc['text'] == 'hello\n'`
- A003 `assert` L29: `doc['literal'] == 'C:\\Users\\Ada'`
- A004 `assert` L30: `doc.as_string() == content`

### `hidden_tests/test_hidden_behavior.py::test_arrays_of_tables_and_inline_tables_dump_correctly`

- mapping: `B003, B004`
- API: `featurelifted.aot, featurelifted.array, featurelifted.exceptions, featurelifted.item`
- risk: `none`
- A001 `assert` L42: `doc.as_string() == dedent('        [[dependency]]\n        name = "requests"\n        version = "^2.31"\n\n        [[dependency]]\n        name = "pytest"\n        version = "^8"\n        optional = true\n        ')`
- A002 `assert` L57: `arr.as_string() == '[{x = 1}, {x = 2}]'`

### `hidden_tests/test_hidden_behavior.py::test_dotted_keys_table_redefinition_and_unicode_errors`

- mapping: `B006`
- API: `featurelifted.exceptions, featurelifted.loads, featurelifted.parse`
- risk: `exception_semantics`
- A001 `assert` L63: `doc['a']['b']['c'] == 1`
- A002 `assert` L64: `doc['site']['google.com'] is True`
- A003 `raises` L66: `pytest.raises(ParseError)`
- A004 `raises` L69: `pytest.raises(InvalidUnicodeValueError)`
- A005 `assert` L72: `excinfo.value.line == 1`
- A006 `assert` L73: `excinfo.value.col == 6`

### `hidden_tests/test_hidden_behavior.py::test_string_constructor_and_sorted_dump_preserve_expected_format`

- mapping: `B001, B004, B005, B007`
- API: `featurelifted.dumps, featurelifted.exceptions, featurelifted.parse, featurelifted.string`
- risk: `ordering_semantics`
- A001 `assert` L81: `basic.as_string() == '"hello \\"world\\""'`
- A002 `assert` L82: `literal.as_string() == "'C:\\Users\\Ada'"`
- A003 `assert` L83: `multiline.as_string() == '"""first\nsecond\n"""'`
- A004 `assert` L86: `dumps(doc, sort_keys=True) == 'aaa = "foo"\nzzz = 1\n'`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B008`
- API: `featurelifted.aot, featurelifted.array, featurelifted.document, featurelifted.dumps, featurelifted.exceptions, featurelifted.inline_table, featurelifted.item, featurelifted.loads, featurelifted.parse, featurelifted.string, featurelifted.table`
- risk: `none`
- A001 `assert` L19: `callable(parse)`
- A002 `assert` L20: `callable(loads)`
- A003 `assert` L21: `callable(dumps)`
- A004 `assert` L22: `callable(document)`
- A005 `assert` L23: `callable(table)`
- A006 `assert` L24: `callable(inline_table)`
- A007 `assert` L25: `callable(array)`
- A008 `assert` L26: `callable(aot)`
- A009 `assert` L27: `callable(string)`
- A010 `assert` L28: `callable(item)`
- A011 `assert` L29: `exceptions is not None`
- A012 `assert` L30: `issubclass(getattr(exceptions, 'InvalidUnicodeValueError'), BaseException)`
- A013 `assert` L31: `issubclass(getattr(exceptions, 'ParseError'), BaseException)`
- A014 `assert` L32: `issubclass(getattr(exceptions, 'UnexpectedCharError'), BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `tomlkit`
- source entrypoints: `tomlkit.parse, tomlkit.loads, tomlkit.dumps, tomlkit.document, tomlkit.table, tomlkit.inline_table, tomlkit.array, tomlkit.aot, tomlkit.string, tomlkit.item, tomlkit.exceptions.ParseError`
- oracle source files: `tomlkit/__init__.py, tomlkit/api.py, tomlkit/container.py, tomlkit/exceptions.py, tomlkit/items.py, tomlkit/parser.py, tomlkit/source.py, tomlkit/toml_document.py, tomlkit/toml_file.py, tomlkit/_compat.py, tomlkit/_types.py, tomlkit/_utils.py`
- runtime dependencies: `none`
- oracle notes: Reference closure for TOML parse/dump and document round-trip behavior. Tests, docs, CI, packaging metadata, and release tooling are intentionally excluded.
