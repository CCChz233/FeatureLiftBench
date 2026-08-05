# tinycss2__stylesheet_roundtrip_core__001

- release: `external50`
- lift: `Adapted`
- coupling: `parser_state_coupling`
- strict validation: `PASS`
- tests/assertions: `9/12`

## Required API

- `featurelifted.parse_stylesheet` (function) `(css: str, skip_comments: bool = False, skip_whitespace: bool = False) -> list`
- `featurelifted.serialize` (function) `(nodes) -> str`
- `featurelifted.ast.QualifiedRule` (class)
- `featurelifted.ast.AtRule` (class)
- `featurelifted.ast.ParseError` (class)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse stylesheet into QualifiedRule/AtRule/ParseError nodes. Required observable cases include parse qualified rule; parse at rule; parse error node not raise.
- **B002**: The extracted feature must support this observable behavior: serialize nodes back to CSS. Required observable cases include roundtrip simple; serialize preserves at keyword.
- **B003**: The extracted feature must support this observable behavior: skip_whitespace option. Required observable cases include skip whitespace option.
- **B004**: QualifiedRule exposes a prelude used by selectors.
- **B005**: The package exposes the required task API paths `featurelifted.parse_stylesheet`, `featurelifted.serialize`, `featurelifted.ast.QualifiedRule`, `featurelifted.ast.AtRule`, `featurelifted.ast.ParseError` with the kinds and callable signatures listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: tinycss2.

## Tests

### `public_tests/test_public_api.py::test_parse_qualified_rule`

- mapping: `B001`
- API: `featurelifted.ast, featurelifted.parse_stylesheet, featurelifted.serialize`
- risk: `none`
- A001 `assert` L9: `nodes`
- A002 `assert` L10: `'div' in serialize(nodes)`

### `public_tests/test_public_api.py::test_roundtrip_simple`

- mapping: `B002`
- API: `featurelifted.ast, featurelifted.parse_stylesheet, featurelifted.serialize`
- risk: `none`
- A001 `assert` L16: `'color' in out and 'blue' in out`

### `public_tests/test_public_api.py::test_parse_at_rule`

- mapping: `B003`
- API: `featurelifted.ast, featurelifted.parse_stylesheet`
- risk: `none`
- A001 `assert` L21: `any((isinstance(n, AtRule) for n in nodes))`

### `hidden_tests/test_hidden_behavior.py::test_skip_whitespace_option`

- mapping: `B001`
- API: `featurelifted.ast, featurelifted.parse_stylesheet`
- risk: `none`
- A001 `assert` L12: `all((not type(n).__name__.endswith('WhitespaceToken') for n in nodes))`

### `hidden_tests/test_hidden_behavior.py::test_serialize_preserves_at_keyword`

- mapping: `B002`
- API: `featurelifted.ast, featurelifted.parse_stylesheet, featurelifted.serialize`
- risk: `none`
- A001 `assert` L17: `'@import' in serialize(parse_stylesheet(css))`

### `hidden_tests/test_hidden_behavior.py::test_parse_error_node_not_raise`

- mapping: `B003`
- API: `featurelifted.ast, featurelifted.parse_stylesheet`
- risk: `none`
- A001 `assert` L22: `any((isinstance(n, ParseError) for n in nodes))`

### `hidden_tests/test_hidden_behavior.py::test_qualified_prelude`

- mapping: `B004`
- API: `featurelifted.ast, featurelifted.parse_stylesheet`
- risk: `none`
- A001 `assert` L27: `q.prelude`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__, featurelifted.ast`
- risk: `filesystem_resource`
- A001 `assert` L36: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.ast, featurelifted.parse_stylesheet, featurelifted.serialize`
- risk: `none`
- A001 `assert` L6: `callable(parse_stylesheet)`
- A002 `assert` L7: `callable(serialize)`
- A003 `assert` L8: `QualifiedRule is not None and AtRule is not None and (ParseError is not None)`

## Dependency / Oracle Evidence

- allowed dependencies: `webencodings`
- forbidden imports: `tinycss2`
- source entrypoints: `none`
- oracle source files: `tinycss2/parser.py, tinycss2/serializer.py, tinycss2/ast.py`
- runtime dependencies: `webencodings`
- oracle notes: Adapted parse_stylesheet/serialize roundtrip.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
