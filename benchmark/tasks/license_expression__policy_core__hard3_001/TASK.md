# FeatureLift Task: License expression parse and policy evaluation

Extract a task-scoped subset of `license-expression` into a standalone `featurelifted` package.

The implementation must not import `license_expression` or `boolean`, must not read from `repo/`, must not use the network, and must not depend on external services. Use only the standard library.

## Target API

```python
from featurelifted import ExpressionInfo, ExpressionParseError, LicenseSymbol, Licensing

LicenseSymbol(key, aliases=(), is_exception=False)
Licensing(symbols=()).parse(expression, validate=False, strict=False)
Licensing(symbols=()).validate(expression)
Licensing(symbols=()).license_symbols(expression)
Licensing(symbols=()).evaluate_policy(expression, allowed=(), denied=())
```

Parsed expression nodes must expose `render()`.

## Required Behavior

- Parse symbols, `AND`, `OR`, `WITH`, and parentheses.
- `AND` binds tighter than `OR`.
- Parentheses override precedence.
- `WITH` binds a license symbol to an exception symbol.
- Aliases normalize to canonical `LicenseSymbol.key` values.
- Exception symbols cannot appear as plain licenses.
- Plain license symbols cannot be used as `WITH` exceptions.
- `validate()` returns `ExpressionInfo` with errors and invalid symbols instead of raising for unknown symbols.
- `evaluate_policy()` returns a dictionary with `status`, `normalized`, `symbols`, `denied`, `unknown`, and `errors`.

## Constraints

- Forbidden imports: `license_expression`, `boolean`.
- Forbidden path access: `repo/`, `src/license_expression/`.
- Do not implement ScanCode/SPDX bundled databases or HTML rendering templates.

## Public vs Hidden Tests

Public tests cover alias normalization, AND/OR precedence, WITH exception normalization, and allowed policy decisions.
Hidden tests cover parentheses precedence, invalid WITH usage, exception-as-license rejection, unknown-symbol validation, denied policy decisions, and unbalanced parentheses.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — LicenseSymbol aliases and exception marker
- **B002** — Licensing.parse
- **B003** — Licensing.validate
- **B004** — Licensing.license_symbols
- **B005** — Licensing.evaluate_policy
- **B006** — AND/OR/WITH parsing
- **B007** — parentheses
- **B008** — alias normalization
- **B009** — unknown symbol and exception placement errors
- **B010** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B011** — the submitted package does not import forbidden upstream packages: license_expression, boolean
<!-- featureliftbench:behavior-clauses:end -->
