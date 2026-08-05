# sqlparse__parse_format_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `FAIL`
- tests/assertions: `9/28`

## Required API

- `featurelifted.parse` (function) `(sql: str, encoding: str | None = None) -> tuple[Statement, ...]`
- `featurelifted.parsestream` (function) `(stream: Union[str, IO[str]], encoding: str | None = None) -> collections.abc.Generator[Statement, None, None]`
- `featurelifted.split` (function) `(sql: str, encoding: str | None = None, strip_semicolon: bool = False) -> list[str]`
- `featurelifted.format` (function) `(sql: str, encoding: str | None = None, **options: Any) -> str`
- `featurelifted.sql` (module)
- `featurelifted.tokens` (module)
- `featurelifted.exceptions` (module)
- `featurelifted.exceptions.SQLParseError` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse SQL text into Statement token trees. Required observable cases include parse returns statement tokens; token navigation and ancestor relationships.
- **B002**: The extracted feature must support this observable behavior: split multi-statement SQL scripts while respecting strings, comments, and nesting. Required observable cases include split respects quoted semicolons; split handles comments and embedded semicolons.
- **B003**: The extracted feature must support this observable behavior: support common token tree traversal and identifier helpers. Required observable cases include format supports common options; cte aliases and identifier helpers.
- **B004**: The extracted feature must support this observable behavior: format common SQL with keyword case, identifier case, comment stripping, reindentation, indentation width, and operator spacing. Required observable cases include format supports common options; formatter comment stripping and spacing; formatter rejects invalid options.
- **B005**: The extracted feature must support this observable behavior: preserve original behavior for comments, whitespace, string literals, aliases, functions, nested expressions, CTEs, CASE expressions, and common DDL/DML. Required observable cases include cte aliases and identifier helpers.
- **B006**: The package exposes the required task API paths `featurelifted.parse`, `featurelifted.parsestream`, `featurelifted.split`, `featurelifted.format`, `featurelifted.sql`, `featurelifted.tokens`, `featurelifted.exceptions`, `featurelifted.exceptions.SQLParseError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_parse_returns_statement_tokens`

- mapping: `B001`
- API: `featurelifted.parse, featurelifted.sql, featurelifted.sql.Statement, featurelifted.tokens, featurelifted.tokens.Keyword, featurelifted.tokens.Keyword.DML`
- risk: `state_mutation`
- A001 `assert` L13: `isinstance(statement, sql.Statement)`
- A002 `assert` L14: `statement.get_type() == 'SELECT'`
- A003 `assert` L16: `flattened[0].value == 'select'`
- A004 `assert` L17: `flattened[0].ttype is T.Keyword.DML`
- A005 `assert` L18: `[token.value for token in flattened[:5]] == ['select', 'id', ',', 'name', 'from']`

### `public_tests/test_public_api.py::test_split_respects_quoted_semicolons`

- mapping: `B002`
- API: `featurelifted.split`
- risk: `none`
- A001 `assert` L24: `split(script, strip_semicolon=True) == ["select ';' as semi", 'select 2']`

### `public_tests/test_public_api.py::test_format_supports_common_options`

- mapping: `B003, B004`
- API: `featurelifted.format`
- risk: `none`
- A001 `assert` L35: `formatted == 'SELECT a,\n       b\nFROM t\nWHERE a = 1\n  AND b = 2'`

### `hidden_tests/test_hidden_behavior.py::test_split_handles_comments_and_embedded_semicolons`

- mapping: `B002`
- API: `featurelifted.exceptions, featurelifted.split`
- risk: `none`
- A001 `assert` L15: `split(script, strip_semicolon=True) == ['select 1; -- keep ; comment', "select ';'"]`

### `hidden_tests/test_hidden_behavior.py::test_cte_aliases_and_identifier_helpers`

- mapping: `B003, B005`
- API: `featurelifted.exceptions, featurelifted.parse, featurelifted.sql, featurelifted.sql.Identifier`
- risk: `none`
- A001 `assert` L27: `statement.get_type() == 'SELECT'`
- A002 `assert` L33: `('cte AS (SELECT id FROM users)', 'cte', 'cte', None) in identifiers`
- A003 `assert` L34: `('cte.id AS user_id', 'user_id', 'id', 'user_id') in identifiers`
- A004 `assert` L35: `('logs', 'logs', 'logs', None) in identifiers`

### `hidden_tests/test_hidden_behavior.py::test_token_navigation_and_ancestor_relationships`

- mapping: `B001`
- API: `featurelifted.exceptions, featurelifted.parse, featurelifted.sql, featurelifted.sql.Comparison, featurelifted.sql.Where`
- risk: `none`
- A001 `assert` L44: `index == 2`
- A002 `assert` L45: `isinstance(comparison, sql.Comparison)`
- A003 `assert` L46: `comparison.value == 'id = 1'`
- A004 `assert` L47: `comparison.within(sql.Where)`
- A005 `assert` L48: `comparison.has_ancestor(where)`

### `hidden_tests/test_hidden_behavior.py::test_formatter_comment_stripping_and_spacing`

- mapping: `B004`
- API: `featurelifted.exceptions, featurelifted.format`
- risk: `none`
- A001 `assert` L52: `format('select a, -- inline\n b from t', strip_comments=True, reindent=True, keyword_case='upper') == 'SELECT a, b\nFROM t'`
- A002 `assert` L62: `format('select a+b as total from t', use_space_around_operators=True) == 'select a + b as total from t'`

### `hidden_tests/test_hidden_behavior.py::test_formatter_rejects_invalid_options`

- mapping: `B004`
- API: `featurelifted.exceptions, featurelifted.format`
- risk: `exact_error_text, exception_semantics`
- A001 `raises` L69: `pytest.raises(SQLParseError, match='Invalid value for keyword_case')`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.exceptions, featurelifted.format, featurelifted.parse, featurelifted.parsestream, featurelifted.split, featurelifted.sql, featurelifted.tokens`
- risk: `none`
- A001 `assert` L15: `callable(parse)`
- A002 `assert` L16: `callable(parsestream)`
- A003 `assert` L17: `callable(split)`
- A004 `assert` L18: `callable(format)`
- A005 `assert` L19: `sql is not None`
- A006 `assert` L20: `tokens is not None`
- A007 `assert` L21: `exceptions is not None`
- A008 `assert` L22: `issubclass(getattr(exceptions, 'SQLParseError'), BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `sqlparse`
- source entrypoints: `sqlparse.parse, sqlparse.parsestream, sqlparse.split, sqlparse.format, sqlparse.sql.Token, sqlparse.sql.TokenList, sqlparse.sql.Statement, sqlparse.sql.Identifier, sqlparse.sql.IdentifierList, sqlparse.tokens`
- oracle source files: `none`
- runtime dependencies: `none`

## Machine Issues

- public_tests/test_public_api.py uses undeclared API reference featurelifted.sql.Statement
- public_tests/test_public_api.py uses undeclared API reference featurelifted.tokens.Keyword
- public_tests/test_public_api.py uses undeclared API reference featurelifted.tokens.Keyword.DML
- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.sql.Comparison
- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.sql.Identifier
- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.sql.Where
