# FeatureLift Task: sqlglot parse transpile

Extract a task-scoped subset of `sqlglot` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    errors,
    exp,
    parse,
    parse_one,
    transpile,
)
```

## Required API Details

- `parse_one(sql: str, read: str | None = None)`
- `parse(sql: str, read: str | None = None)`
- `transpile(sql: str, read: str | None = None, write: str | None = None, pretty: bool = False)`
- `exp.Select` class must be importable
- `exp.Column` class must be importable
- `errors.ParseError` must be importable and raisable

## Required Behavior

- The extracted feature must support this observable behavior: parse_one/parse into Select expressions and raise ParseError on invalid SQL. Required observable cases include parse one select; parse error; parse multiple.
- The extracted feature must support this observable behavior: transpile across sqlite/postgres/mysql. Required observable cases include transpile sqlite to postgres; transpile mysql to sqlite; mysql dialect backticks.
- The extracted feature must support this observable behavior: Expression.sql with pretty formatting. Required observable cases include pretty sql.
- Frozen dialects for required tests are sqlite, postgres, and mysql only.
- The package exposes the required task API paths `featurelifted.parse_one`, `featurelifted.parse`, `featurelifted.transpile`, `featurelifted.exp.Select`, `featurelifted.exp.Column`, `featurelifted.errors.ParseError` with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: sqlglot.

## Constraints

- Forbidden imports: `sqlglot`.
- Do not implement optimizer suite.
- Do not implement execute against DB.
- Do not implement original sqlglot import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: parse_one/parse into Select expressions and raise ParseError on invalid SQL. Required observable cases include parse one select; parse error; parse multiple.
- **B002** — The extracted feature must support this observable behavior: transpile across sqlite/postgres/mysql. Required observable cases include transpile sqlite to postgres; transpile mysql to sqlite; mysql dialect backticks.
- **B003** — The extracted feature must support this observable behavior: Expression.sql with pretty formatting. Required observable cases include pretty sql.
- **B004** — Frozen dialects for required tests are sqlite, postgres, and mysql only.
- **B005** — The package exposes the required task API paths `featurelifted.parse_one`, `featurelifted.parse`, `featurelifted.transpile`, `featurelifted.exp.Select`, `featurelifted.exp.Column`, `featurelifted.errors.ParseError` with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: sqlglot.
<!-- featureliftbench:behavior-clauses:end -->
