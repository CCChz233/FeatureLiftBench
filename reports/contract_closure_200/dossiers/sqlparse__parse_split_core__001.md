# sqlparse__parse_split_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `FAIL`
- tests/assertions: `5/15`

## Required API

- `featurelifted.parse` (function) `(sql: str, encoding: str | None = None) -> tuple[Statement, ...]`
- `featurelifted.parsestream` (function) `(stream: Union[str, IO[str]], encoding: str | None = None) -> collections.abc.Generator[Statement, None, None]`
- `featurelifted.split` (function) `(sql: str, encoding: str | None = None, strip_semicolon: bool = False) -> list[str]`
- `featurelifted.sql` (module)
- `featurelifted.tokens` (module)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse SQL text into Statement token trees. Required observable cases include parse returns statement tokens; parse multiple statements.
- **B002**: The extracted feature must support this observable behavior: split multi-statement SQL scripts while respecting strings, comments, and nesting. Required observable cases include split respects quoted semicolons; split handles comments and embedded semicolons.
- **B003**: The extracted feature must support this observable behavior: preserve statement-splitting behavior for semicolons inside quotes and comments. Required observable cases include split handles comments and embedded semicolons.
- **B004**: The package exposes the required task API paths `featurelifted.parse`, `featurelifted.parsestream`, `featurelifted.split`, `featurelifted.sql`, `featurelifted.tokens` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_parse_returns_statement_tokens`

- mapping: `B001`
- API: `featurelifted.parse, featurelifted.sql, featurelifted.sql.Statement, featurelifted.tokens, featurelifted.tokens.Keyword, featurelifted.tokens.Keyword.DML`
- risk: `state_mutation`
- A001 `assert` L12: `isinstance(statement, sql.Statement)`
- A002 `assert` L13: `statement.get_type() == 'SELECT'`
- A003 `assert` L15: `flattened[0].value == 'select'`
- A004 `assert` L16: `flattened[0].ttype is T.Keyword.DML`
- A005 `assert` L17: `[token.value for token in flattened[:5]] == ['select', 'id', ',', 'name', 'from']`

### `public_tests/test_public_api.py::test_split_respects_quoted_semicolons`

- mapping: `B002`
- API: `featurelifted.split`
- risk: `none`
- A001 `assert` L23: `split(script, strip_semicolon=True) == ["select ';' as semi", 'select 2']`

### `hidden_tests/test_hidden_behavior.py::test_split_handles_comments_and_embedded_semicolons`

- mapping: `B002, B003`
- API: `featurelifted.split`
- risk: `none`
- A001 `assert` L10: `split(script, strip_semicolon=True) == ['select 1; -- keep ; comment', "select ';'"]`

### `hidden_tests/test_hidden_behavior.py::test_parse_multiple_statements`

- mapping: `B001`
- API: `featurelifted.parse`
- risk: `state_mutation`
- A001 `assert` L19: `len(statements) == 2`
- A002 `assert` L20: `statements[0].get_type() == 'SELECT'`
- A003 `assert` L21: `statements[1].get_type() == 'SELECT'`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.parse, featurelifted.parsestream, featurelifted.split, featurelifted.sql, featurelifted.tokens`
- risk: `none`
- A001 `assert` L13: `callable(parse)`
- A002 `assert` L14: `callable(parsestream)`
- A003 `assert` L15: `callable(split)`
- A004 `assert` L16: `sql is not None`
- A005 `assert` L17: `tokens is not None`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `sqlparse`
- source entrypoints: `sqlparse.parse, sqlparse.parsestream, sqlparse.split`
- oracle source files: `none`
- runtime dependencies: `none`
- oracle notes: Parse and split closure only. Formatter filters, CLI, tests, docs, and packaging metadata are excluded.

## Machine Issues

- public_tests/test_public_api.py uses undeclared API reference featurelifted.sql.Statement
- public_tests/test_public_api.py uses undeclared API reference featurelifted.tokens.Keyword
- public_tests/test_public_api.py uses undeclared API reference featurelifted.tokens.Keyword.DML
