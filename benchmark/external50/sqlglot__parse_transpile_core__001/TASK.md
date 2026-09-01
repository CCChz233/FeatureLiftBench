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

- parse_one returns an exp.Select whose sql() reproduces a simple SELECT statement, parse returns one exp.Select per semicolon-separated statement, and malformed SQL such as `SELECT FROM` raises ParseError.
- transpile converts SELECT statements between the sqlite, postgres, and mysql dialects and returns a non-empty list of SQL strings; mysql backtick-quoted identifiers can be parsed and rendered.
- Expression.sql(pretty=True) returns formatted SQL that retains the SELECT projection and FROM clause.
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

- **B001** — parse_one returns an exp.Select whose sql() reproduces a simple SELECT statement, parse returns one exp.Select per semicolon-separated statement, and malformed SQL such as `SELECT FROM` raises ParseError.
- **B002** — transpile converts SELECT statements between the sqlite, postgres, and mysql dialects and returns a non-empty list of SQL strings; mysql backtick-quoted identifiers can be parsed and rendered.
- **B003** — Expression.sql(pretty=True) returns formatted SQL that retains the SELECT projection and FROM clause.
- **B004** — Frozen dialects for required tests are sqlite, postgres, and mysql only.
- **B005** — The package exposes the required task API paths `featurelifted.parse_one`, `featurelifted.parse`, `featurelifted.transpile`, `featurelifted.exp.Select`, `featurelifted.exp.Column`, `featurelifted.errors.ParseError` with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: sqlglot.
<!-- featureliftbench:behavior-clauses:end -->
