# FeatureLift Task: boolean parse simplify

Extract a task-scoped subset of `boolean.py` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    BooleanAlgebra,
    Expression,
    ParseError,
    Symbol,
)
```

## Required API Details

- `BooleanAlgebra` class must be importable
  - `BooleanAlgebra.parse(self, expr, simplify=False)`
  - `BooleanAlgebra.Symbol` attribute must exist on instances
  - `BooleanAlgebra.TRUE` attribute must exist on instances
  - `BooleanAlgebra.FALSE` attribute must exist on instances
- `BooleanAlgebra.parse(self, expr, simplify=False)`
- `ParseError` class must be importable
- `Symbol` class must be importable
- `Expression` class must be importable
  - `Expression.simplify(self)`
  - `Expression.subs(self, substitutions, default=None, simplify=False)`

## Required Behavior

- Given a boolean expression containing symbols, conjunction, disjunction, and negation, `BooleanAlgebra.parse` builds an expression whose `simplify` method returns the equivalent canonical expression.
- Given a parsed expression and a mapping from an algebra `Symbol` to `TRUE`, `Expression.subs` replaces that symbol, and with `simplify=True` returns the simplified substituted expression.
- Simplifying expressions that differ only in commutative operand order produces equal results, while parsing an expression that ends with an operator raises `ParseError`.
- When the parsed expression negates the `TRUE` constant, calling `simplify` returns the algebra's `FALSE` constant.
- The package exposes BooleanAlgebra/parse/ParseError/Symbol with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: boolean.

## Constraints

- Forbidden imports: `boolean`.
- Do not implement SAT solvers.
- Do not implement original boolean import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — Given a boolean expression containing symbols, conjunction, disjunction, and negation, `BooleanAlgebra.parse` builds an expression whose `simplify` method returns the equivalent canonical expression.
- **B002** — Given a parsed expression and a mapping from an algebra `Symbol` to `TRUE`, `Expression.subs` replaces that symbol, and with `simplify=True` returns the simplified substituted expression.
- **B003** — Simplifying expressions that differ only in commutative operand order produces equal results, while parsing an expression that ends with an operator raises `ParseError`.
- **B004** — When the parsed expression negates the `TRUE` constant, calling `simplify` returns the algebra's `FALSE` constant.
- **B005** — The package exposes BooleanAlgebra/parse/ParseError/Symbol with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: boolean.
<!-- featureliftbench:behavior-clauses:end -->
