# license_expression__policy_core__hard3_001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `10/25`

## Required API

- `featurelifted.LicenseSymbol` (class) `(key: 'str', aliases: 'tuple[str, ...] | list[str]' = (), is_exception: 'bool' = False) -> 'None'`
- `featurelifted.LicenseSymbol.key` (attribute)
- `featurelifted.Licensing` (class) `(symbols: 'tuple[LicenseSymbol | str, ...] | list[LicenseSymbol | str]' = ()) -> 'None'`
- `featurelifted.Licensing.parse` (method) `(self, expression: 'str', validate: 'bool' = False, strict: 'bool' = False) -> 'Node'`
- `featurelifted.Licensing.validate` (method) `(self, expression: 'str') -> 'ExpressionInfo'`
- `featurelifted.Licensing.license_symbols` (method) `(self, expression: 'str | Node') -> 'list[LicenseSymbol]'`
- `featurelifted.Licensing.evaluate_policy` (method) `(self, expression: 'str', allowed: 'tuple[str, ...] | list[str] | set[str]' = (), denied: 'tuple[str, ...] | list[str] | set[str]' = ()) -> 'dict[str, Any]'`
- `featurelifted.ExpressionInfo` (class) `(original_expression: 'str', normalized_expression: 'str | None' = None, errors: 'list[str] | None' = None, invalid_symbols: 'list[str] | None' = None) -> None`
- `featurelifted.ExpressionParseError` (exception)

## Public Behaviors

- **B001**: Parse symbols, `AND`, `OR`, `WITH`, and parentheses.
- **B002**: `AND` binds tighter than `OR`.
- **B003**: Parentheses override precedence.
- **B004**: `WITH` binds a license symbol to an exception symbol.
- **B005**: Aliases normalize to canonical `LicenseSymbol.key` values.
- **B006**: Exception symbols cannot appear as plain licenses.
- **B007**: Plain license symbols cannot be used as `WITH` exceptions.
- **B008**: `validate()` returns `ExpressionInfo` with errors and invalid symbols instead of raising for unknown symbols.
- **B009**: `evaluate_policy()` returns a dictionary with `status`, `normalized`, `symbols`, `denied`, `unknown`, and `errors`.
- **B010**: The package exposes the required task API paths `featurelifted.LicenseSymbol`, `featurelifted.LicenseSymbol.key`, `featurelifted.Licensing`, `featurelifted.Licensing.parse`, `featurelifted.Licensing.validate`, `featurelifted.Licensing.license_symbols`, `featurelifted.Licensing.evaluate_policy`, `featurelifted.ExpressionInfo`, `featurelifted.ExpressionParseError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_alias_normalization_and_precedence_rendering`

- mapping: `B008`
- API: `none detected`
- risk: `none`
- A001 `assert` L20: `parsed.render() == 'GPL-2.0-only OR (Apache-2.0 AND MIT)'`
- A002 `assert` L21: `[symbol.key for symbol in licensing.license_symbols(parsed)] == ['GPL-2.0-only', 'Apache-2.0', 'MIT']`

### `public_tests/test_public_contract.py::test_with_exception_normalizes_aliases`

- mapping: `B001`
- API: `none detected`
- risk: `none`
- A001 `assert` L29: `parsed.render() == 'GPL-2.0-only WITH Classpath-exception-2.0'`

### `public_tests/test_public_contract.py::test_policy_allows_known_allowed_symbols`

- mapping: `B004, B005`
- API: `none detected`
- risk: `none`
- A001 `assert` L41: `result['status'] == 'allowed'`
- A002 `assert` L42: `result['normalized'] == 'Apache-2.0 AND MIT'`

### `hidden_tests/test_hidden_contract.py::test_parentheses_override_precedence`

- mapping: `B007`
- API: `none detected`
- risk: `none`
- A001 `assert` L23: `parsed.render() == '(MIT OR BSD-3-Clause) AND Apache-2.0'`

### `hidden_tests/test_hidden_contract.py::test_plain_symbol_cannot_be_used_as_with_exception`

- mapping: `B009`
- API: `featurelifted.ExpressionParseError`
- risk: `exact_error_text, exception_semantics`
- A001 `raises` L29: `pytest.raises(ExpressionParseError, match='plain license symbol')`

### `hidden_tests/test_hidden_contract.py::test_exception_symbol_cannot_be_used_as_plain_license`

- mapping: `B004, B009`
- API: `featurelifted.ExpressionParseError`
- risk: `exact_error_text, exception_semantics`
- A001 `raises` L36: `pytest.raises(ExpressionParseError, match='exception symbol')`

### `hidden_tests/test_hidden_contract.py::test_validate_reports_unknown_symbol_without_normalized_expression`

- mapping: `B001, B003, B006, B008, B009`
- API: `none detected`
- risk: `none`
- A001 `assert` L45: `info.normalized_expression is None`
- A002 `assert` L46: `info.invalid_symbols == ['UnknownLicense']`
- A003 `assert` L47: `info.errors == ['Unknown license symbol: UnknownLicense']`

### `hidden_tests/test_hidden_contract.py::test_policy_denies_denied_symbol_even_inside_with_expression`

- mapping: `B005, B009`
- API: `none detected`
- risk: `none`
- A001 `assert` L59: `result['status'] == 'denied'`
- A002 `assert` L60: `result['denied'] == ['GPL-2.0-only']`
- A003 `assert` L61: `result['normalized'] == 'GPL-2.0-only WITH Classpath-exception-2.0 OR MIT'`

### `hidden_tests/test_hidden_contract.py::test_unbalanced_parentheses_raise_parse_error`

- mapping: `B002, B009`
- API: `featurelifted.ExpressionParseError`
- risk: `exact_error_text, exception_semantics`
- A001 `raises` L67: `pytest.raises(ExpressionParseError, match='unbalanced')`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B010`
- API: `featurelifted.ExpressionInfo, featurelifted.ExpressionParseError, featurelifted.LicenseSymbol, featurelifted.Licensing`
- risk: `none`
- A001 `assert` L12: `isinstance(LicenseSymbol, type)`
- A002 `assert` L13: `LicenseSymbol is not None`
- A003 `assert` L14: `isinstance(Licensing, type)`
- A004 `assert` L15: `hasattr(Licensing, 'parse')`
- A005 `assert` L16: `hasattr(Licensing, 'validate')`
- A006 `assert` L17: `hasattr(Licensing, 'license_symbols')`
- A007 `assert` L18: `hasattr(Licensing, 'evaluate_policy')`
- A008 `assert` L19: `isinstance(ExpressionInfo, type)`
- A009 `assert` L20: `issubclass(ExpressionParseError, BaseException)`
- A010 `assert` L22: `hasattr(license_symbol, 'key')`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `license_expression, boolean`
- source entrypoints: `license_expression.Licensing, license_expression.LicenseSymbol, license_expression.ExpressionInfo, license_expression.ExpressionParseError`
- oracle source files: `repo/src/license_expression/__init__.py, repo/src/license_expression/_pyahocorasick.py, repo/pyproject.toml, repo/LICENSE`
- runtime dependencies: `none`
- oracle notes: Task-scoped parser and policy evaluator. ScanCode/SPDX bundled datasets, boolean.py dependency, and HTML rendering are intentionally excluded.
