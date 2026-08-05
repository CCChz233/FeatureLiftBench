# parse__format_parser_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `5/12`

## Required API

- `featurelifted.Parser` (class) `(format, case_sensitive=False)`
- `featurelifted.Result` (class) `(fixed: tuple, named: dict) -> None`
- `featurelifted.compile` (function) `(format, case_sensitive=False)`
- `featurelifted.parse` (function) `(format, string, case_sensitive=False)`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: literal and escaped-brace matching. Required observable cases include named and typed fields; positional and escaped braces; full match and case policy; word and default boundaries.
- **B002**: The extracted feature must support this observable behavior: named and positional capture fields. Required observable cases include named and typed fields; positional and escaped braces; full match and case policy; word and default boundaries.
- **B003**: The extracted feature must support this observable behavior: integer, float, word, and default string conversions. Required observable cases include named and typed fields; positional and escaped braces; full match and case policy; word and default boundaries.
- **B004**: The extracted feature must support this observable behavior: case-sensitive option and full-string matching. Required observable cases include named and typed fields; positional and escaped braces; full match and case policy; word and default boundaries.
- **B005**: The package exposes the required task API paths `featurelifted.Parser`, `featurelifted.Result`, `featurelifted.compile`, `featurelifted.parse` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_named_and_typed_fields`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.parse`
- risk: `none`
- A001 `assert` L5: `result.named == {'name': 'Ada', 'age': 37}`
- A002 `assert` L6: `result.fixed == ()`

### `public_tests/test_public_contract.py::test_positional_and_escaped_braces`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.compile`
- risk: `none`
- A001 `assert` L11: `result.fixed == (3, 2.5)`

### `hidden_tests/test_hidden_contract.py::test_full_match_and_case_policy`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.parse`
- risk: `none`
- A001 `assert` L4: `parse('Hello {name}', 'hello Ada').named['name'] == 'Ada'`
- A002 `assert` L5: `parse('Hello {name}', 'hello Ada', case_sensitive=True) is None`
- A003 `assert` L6: `parse('x={:d}', 'prefix x=1') is None`

### `hidden_tests/test_hidden_contract.py::test_word_and_default_boundaries`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.parse`
- risk: `none`
- A001 `assert` L10: `result.named == {'first': 'alpha', 'second': 'rest-of-value'}`
- A002 `assert` L11: `result[0] == 'alpha'`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.Parser, featurelifted.Result, featurelifted.compile, featurelifted.parse`
- risk: `none`
- A001 `assert` L12: `isinstance(Parser, type)`
- A002 `assert` L13: `isinstance(Result, type)`
- A003 `assert` L14: `callable(compile)`
- A004 `assert` L15: `callable(parse)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `parse`
- source entrypoints: `parse.parse, parse.compile, parse.Parser, parse.Result`
- oracle source files: `parse.parse, parse.compile, parse.Parser, parse.Result`
- runtime dependencies: `none`
- oracle notes: Entrypoints are maintainer-private provenance and are never Agent-visible in Main.
- behavior contract lacks a completed review_status
