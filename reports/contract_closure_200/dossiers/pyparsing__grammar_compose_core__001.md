# pyparsing__grammar_compose_core__001

- release: `external50`
- lift: `Adapted`
- coupling: `parser_state_coupling`
- strict validation: `PASS`
- tests/assertions: `9/31`

## Required API

- `featurelifted.Word` (class)
- `featurelifted.Word.parse_string` (method)
- `featurelifted.Literal` (class)
- `featurelifted.Literal.parse_string` (method)
- `featurelifted.Keyword` (class)
- `featurelifted.Regex` (class)
- `featurelifted.Optional` (class)
- `featurelifted.ZeroOrMore` (class)
- `featurelifted.OneOrMore` (class)
- `featurelifted.OneOrMore.parse_string` (method)
- `featurelifted.Group` (class)
- `featurelifted.Group.parse_string` (method)
- `featurelifted.Suppress` (class)
- `featurelifted.ParseException` (exception)
- `featurelifted.ParseResults` (class)
- `featurelifted.ParseResults.as_list` (method)
- `featurelifted.ParseResults.as_dict` (method)
- `featurelifted.alphas` (constant)
- `featurelifted.nums` (constant)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: compose Word/Literal/Optional/Group helpers and parse_string with named results. Required observable cases include word literal compose; optional group.
- **B002**: The extracted feature must support this observable behavior: Keyword/Regex/ZeroOrMore/OneOrMore/Suppress composition. Required observable cases include keyword and regex; zero one or more; group structure.
- **B003**: The extracted feature must support this observable behavior: ParseException on mismatch including parse_all leftovers. Required observable cases include parse exception; parse all flag.
- **B004**: ParseResults supports as_list/as_dict accessors used in tests.
- **B005**: The package exposes the required task API paths for Word/Literal/Keyword/Regex/Optional/ZeroOrMore/OneOrMore/Group/Suppress/ParseException/ParseResults/alphas/nums with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: pyparsing.

## Tests

### `public_tests/test_public_api.py::test_word_literal_compose`

- mapping: `B001`
- API: `featurelifted.Literal, featurelifted.Word, featurelifted.alphas`
- risk: `none`
- A001 `assert` L9: `result.as_dict()['name'] == 'Hello'`
- A002 `assert` L10: `result.as_list()[0] == 'Hello'`

### `public_tests/test_public_api.py::test_optional_group`

- mapping: `B002`
- API: `featurelifted.Literal, featurelifted.Optional, featurelifted.Word, featurelifted.alphas`
- risk: `none`
- A001 `assert` L15: `grammar.parse_string('hi').as_list() == ['hi']`
- A002 `assert` L16: `'bang' in grammar.parse_string('hi!').as_dict()`

### `public_tests/test_public_api.py::test_parse_exception`

- mapping: `B003`
- API: `featurelifted.Literal, featurelifted.ParseException`
- risk: `none`
- A001 `assert` L23: `False`
- A002 `assert` L25: `exc.loc >= 0`

### `hidden_tests/test_hidden_behavior.py::test_keyword_and_regex`

- mapping: `B001`
- API: `featurelifted.Keyword, featurelifted.Regex`
- risk: `none`
- A001 `assert` L22: `grammar.parse_string('select name').as_dict()['col'] == 'name'`

### `hidden_tests/test_hidden_behavior.py::test_zero_one_or_more`

- mapping: `B002`
- API: `featurelifted.OneOrMore, featurelifted.Suppress, featurelifted.Word, featurelifted.ZeroOrMore, featurelifted.alphas, featurelifted.nums`
- risk: `none`
- A001 `assert` L27: `grammar.parse_string('a,b,c').as_list() == ['a', 'b', 'c']`
- A002 `assert` L29: `grammar2.parse_string('1 2 3').as_list() == ['1', '2', '3']`

### `hidden_tests/test_hidden_behavior.py::test_group_structure`

- mapping: `B003`
- API: `featurelifted.Group, featurelifted.Word, featurelifted.alphas, featurelifted.nums`
- risk: `none`
- A001 `assert` L35: `result.as_list() == [['x', '9']]`

### `hidden_tests/test_hidden_behavior.py::test_parse_all_flag`

- mapping: `B004`
- API: `featurelifted.ParseException, featurelifted.Word, featurelifted.alphas`
- risk: `none`
- A001 `assert` L42: `False`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L53: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.Group, featurelifted.Group.parse_string, featurelifted.Literal, featurelifted.Literal.parse_string, featurelifted.OneOrMore, featurelifted.OneOrMore.parse_string, featurelifted.ParseResults, featurelifted.ParseResults.as_dict, featurelifted.ParseResults.as_list, featurelifted.Word, featurelifted.Word.parse_string`
- risk: `none`
- A001 `assert` L5: `hasattr(featurelifted, 'Group')`
- A002 `assert` L6: `hasattr(featurelifted, 'Keyword')`
- A003 `assert` L7: `hasattr(featurelifted, 'Literal')`
- A004 `assert` L8: `hasattr(featurelifted, 'OneOrMore')`
- A005 `assert` L9: `hasattr(featurelifted, 'Optional')`
- A006 `assert` L10: `hasattr(featurelifted, 'ParseException')`
- A007 `assert` L11: `hasattr(featurelifted, 'ParseResults')`
- A008 `assert` L12: `hasattr(featurelifted, 'Regex')`
- A009 `assert` L13: `hasattr(featurelifted, 'Suppress')`
- A010 `assert` L14: `hasattr(featurelifted, 'Word')`
- A011 `assert` L15: `hasattr(featurelifted, 'ZeroOrMore')`
- A012 `assert` L16: `hasattr(featurelifted, 'alphas')`
- A013 `assert` L17: `hasattr(featurelifted, 'nums')`
- A014 `assert` L18: `callable(featurelifted.Word.parse_string)`
- A015 `assert` L19: `callable(featurelifted.Literal.parse_string)`
- A016 `assert` L20: `callable(featurelifted.OneOrMore.parse_string)`
- A017 `assert` L21: `callable(featurelifted.Group.parse_string)`
- A018 `assert` L22: `callable(featurelifted.ParseResults.as_list)`
- A019 `assert` L23: `callable(featurelifted.ParseResults.as_dict)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `pyparsing`
- source entrypoints: `none`
- oracle source files: `pyparsing/core.py, pyparsing/results.py, pyparsing/exceptions.py`
- runtime dependencies: `none`
- oracle notes: Adapted ParserElement composition helpers.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
