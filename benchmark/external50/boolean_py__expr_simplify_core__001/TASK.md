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
  - `BooleanAlgebra.parse` callable must exist
  - `BooleanAlgebra.Symbol` attribute must exist on instances
  - `BooleanAlgebra.TRUE` attribute must exist on instances
  - `BooleanAlgebra.FALSE` attribute must exist on instances
- `BooleanAlgebra.parse` callable must exist
- `ParseError` class must be importable
- `Symbol` class must be importable
- `Expression` class must be importable
  - `Expression.simplify` callable must exist
  - `Expression.subs` callable must exist

## Required Behavior

- The extracted feature must support this observable behavior: parse and simplify boolean expressions. Required observable cases include parse and simplify.
- The extracted feature must support this observable behavior: expression.subs with simplify. Required observable cases include subs.
- The extracted feature must support this observable behavior: simplified equality and ParseError on bad input. Required observable cases include equality; parse error.
- NOT/TRUE/FALSE constants simplify as upstream.
- The package exposes BooleanAlgebra/parse/ParseError/Symbol with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: boolean.

## Constraints

- Forbidden imports: `boolean`.
- Do not implement SAT solvers.
- Do not implement original boolean import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: parse and simplify boolean expressions. Required observable cases include parse and simplify.
- **B002** — The extracted feature must support this observable behavior: expression.subs with simplify. Required observable cases include subs.
- **B003** — The extracted feature must support this observable behavior: simplified equality and ParseError on bad input. Required observable cases include equality; parse error.
- **B004** — NOT/TRUE/FALSE constants simplify as upstream.
- **B005** — The package exposes BooleanAlgebra/parse/ParseError/Symbol with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: boolean.
<!-- featureliftbench:behavior-clauses:end -->
