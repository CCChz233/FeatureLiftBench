# FeatureLift Task: Pandas DataFrameSchema validation

Build a standalone `featurelifted` package providing pandas `DataFrameSchema` validation with column dtypes, coerce, and `Check.ge`.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    Check,
    Column,
    DataFrameSchema,
    errors,
)
```

## Required API Details

- `DataFrameSchema(columns=None, checks=None, parsers=None, index=None, dtype=None, coerce=False, strict=False, name=None, ordered=False, unique=None, report_duplicates='all', unique_column_names=False, add_missing_columns=False, title=None, description=None, metadata=None, drop_invalid_rows=False)` class constructor
  - `DataFrameSchema.__init__(self, columns=None, checks=None, parsers=None, index=None, dtype=None, coerce=False, strict=False, name=None, ordered=False, unique=None, report_duplicates='all', unique_column_names=False, add_missing_columns=False, title=None, description=None, metadata=None, drop_invalid_rows=False)`
  - `DataFrameSchema.validate(self, check_obj, head=None, tail=None, sample=None, random_state=None, lazy=False, inplace=False)`
- `Column(dtype=None, checks=None, parsers=None, nullable=False, unique=False, report_duplicates='all', coerce=False, required=True, name=None, regex=False, title=None, description=None, default=None, metadata=None, drop_invalid_rows=False)` class constructor
  - `Column.__init__(self, dtype=None, checks=None, parsers=None, nullable=False, unique=False, report_duplicates='all', coerce=False, required=True, name=None, regex=False, title=None, description=None, default=None, metadata=None, drop_invalid_rows=False)`
- `Check` class must be importable
  - `Check.ge(cls, min_value, **kwargs)`
- `errors.SchemaError` must be importable and raisable

## Required Behavior

- A `DataFrameSchema` whose columns declare dtypes validates a pandas DataFrame whose values already match those dtypes and returns a DataFrame with the same column names.
- When a `Column` is constructed with `coerce=True` and a numeric dtype, `validate` converts compatible string values in that column to the declared dtype.
- A column check created with `Check.ge(min_value)` rejects rows whose values are below `min_value` by raising `featurelifted.errors.SchemaError`.
- Validating a DataFrame that omits a required schema column raises `featurelifted.errors.SchemaError`.
- The package exposes `DataFrameSchema`, `Column`, `Check`, `Check.ge`, `DataFrameSchema.validate`, and `errors.SchemaError` with the callable paths listed in this contract.
- The submitted package source does not import the forbidden upstream package `pandera`.

## Constraints

- Forbidden imports: `pandera`.
- Do not implement Spark/Dask/Polars/Ibis backends.
- Do not implement cloud IO.
- Do not implement CLI infer/generate.
- Do not implement runtime import of pandera.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — A `DataFrameSchema` whose columns declare dtypes validates a pandas DataFrame whose values already match those dtypes and returns a DataFrame with the same column names.
- **B002** — When a `Column` is constructed with `coerce=True` and a numeric dtype, `validate` converts compatible string values in that column to the declared dtype.
- **B003** — A column check created with `Check.ge(min_value)` rejects rows whose values are below `min_value` by raising `featurelifted.errors.SchemaError`.
- **B004** — Validating a DataFrame that omits a required schema column raises `featurelifted.errors.SchemaError`.
- **B005** — The package exposes `DataFrameSchema`, `Column`, `Check`, `Check.ge`, `DataFrameSchema.validate`, and `errors.SchemaError` with the callable paths listed in this contract.
- **B006** — The submitted package source does not import the forbidden upstream package `pandera`.
<!-- featureliftbench:behavior-clauses:end -->
