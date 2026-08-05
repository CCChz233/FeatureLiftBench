# xmltodict__xml_parse_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `12/15`

## Required API

- `featurelifted.parse` (module)
- `featurelifted.unparse` (module)
- `featurelifted.ParsingInterrupted` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse XML strings into ordered dicts with @ attribute prefix. Required observable cases include simple parse text node; parse attributes default prefix; parse repeated siblings become list; roundtrip simple document; custom attr prefix parse.
- **B002**: The extracted feature must support this observable behavior: unparse dicts back to XML with matching attr_prefix and cdata_key. Required observable cases include unparse simple element; roundtrip simple document; unparse custom attr prefix roundtrip.
- **B003**: The extracted feature must support this observable behavior: duplicate sibling elements become lists. Required observable cases include parse repeated siblings become list; unparse custom attr prefix roundtrip.
- **B004**: The extracted feature must support this observable behavior: process_namespaces with optional namespace URI collapse map. Required observable cases include namespace collapse map.
- **B005**: The extracted feature must support this observable behavior: mixed content via #text alongside child elements. Required observable cases include simple parse text node; unparse simple element; semi structured mixed content; force cdata wraps text nodes.
- **B006**: The extracted feature must support this observable behavior: custom attr_prefix and cdata_key options. Required observable cases include custom attr prefix parse; unparse custom attr prefix roundtrip; force cdata wraps text nodes.
- **B007**: The package exposes the required task API paths `featurelifted.parse`, `featurelifted.unparse`, `featurelifted.ParsingInterrupted` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_simple_parse_text_node`

- mapping: `B001, B005`
- API: `featurelifted.parse`
- risk: `none`
- A001 `assert` L7: `parse('<a>data</a>') == {'a': 'data'}`

### `public_tests/test_public_api.py::test_parse_attributes_default_prefix`

- mapping: `B001`
- API: `featurelifted.parse`
- risk: `none`
- A001 `assert` L11: `parse('<a href="xyz"/>') == {'a': {'@href': 'xyz'}}`

### `public_tests/test_public_api.py::test_parse_repeated_siblings_become_list`

- mapping: `B001, B003`
- API: `featurelifted.parse`
- risk: `none`
- A001 `assert` L16: `parse(xml) == {'a': {'b': ['1', '2', '3']}}`

### `public_tests/test_public_api.py::test_unparse_simple_element`

- mapping: `B002, B005`
- API: `featurelifted.unparse`
- risk: `none`
- A001 `assert` L21: `'<greeting>hello</greeting>' in xml`

### `public_tests/test_public_api.py::test_roundtrip_simple_document`

- mapping: `B001, B002`
- API: `featurelifted.parse, featurelifted.unparse`
- risk: `none`
- A001 `assert` L27: `reparsed == original`

### `hidden_tests/test_hidden_behavior.py::test_namespace_collapse_map`

- mapping: `B004`
- API: `featurelifted.parse`
- risk: `none`
- A001 `assert` L36: `parse(xml, process_namespaces=True, namespaces=namespaces) == expected`

### `hidden_tests/test_hidden_behavior.py::test_custom_attr_prefix_parse`

- mapping: `B001, B006`
- API: `featurelifted.parse`
- risk: `none`
- A001 `assert` L40: `parse('<a href="xyz"/>', attr_prefix='!') == {'a': {'!href': 'xyz'}}`

### `hidden_tests/test_hidden_behavior.py::test_semi_structured_mixed_content`

- mapping: `B005`
- API: `featurelifted.parse`
- risk: `none`
- A001 `assert` L45: `parse(xml) == {'a': {'b': None, '#text': 'abcdef'}}`

### `hidden_tests/test_hidden_behavior.py::test_unparse_custom_attr_prefix_roundtrip`

- mapping: `B002, B003, B006`
- API: `featurelifted.parse, featurelifted.unparse`
- risk: `none`
- A001 `assert` L51: `'kind="book"' in xml`
- A002 `assert` L52: `parse(xml, attr_prefix='!') == doc`

### `hidden_tests/test_hidden_behavior.py::test_force_cdata_wraps_text_nodes`

- mapping: `B005, B006`
- API: `featurelifted.parse`
- risk: `none`
- A001 `assert` L56: `parse('<a>data</a>', force_cdata=True) == {'a': {'#text': 'data'}}`

### `hidden_tests/test_hidden_behavior.py::test_no_xmltodict_import_surface`

- mapping: `B008`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L66: `not import_pattern.search(text)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B007`
- API: `featurelifted.ParsingInterrupted, featurelifted.parse, featurelifted.unparse`
- risk: `none`
- A001 `assert` L11: `parse is not None`
- A002 `assert` L12: `unparse is not None`
- A003 `assert` L13: `issubclass(ParsingInterrupted, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `xmltodict`
- source entrypoints: `xmltodict.parse, xmltodict.unparse, xmltodict.ParsingInterrupted, xmltodict._DictSAXHandler, xmltodict._emit, xmltodict._process_namespace`
- oracle source files: `xmltodict.py`
- runtime dependencies: `none`
- oracle notes: Oracle splits single-file xmltodict.py into exceptions, sax_handler, validation, parse, and unparse modules; omits streaming CLI and comment processing.
