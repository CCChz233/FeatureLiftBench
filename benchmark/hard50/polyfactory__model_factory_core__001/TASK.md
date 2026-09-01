# FeatureLift Task: Dataclass model factories

Build a standalone `featurelifted` package providing dataclass factories with overrides, `Use` fields, and batch construction.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    ConfigurationException,
    DataclassFactory,
    Use,
)
```

## Required API Details

- `DataclassFactory` class must be importable
  - `DataclassFactory.build(cls, **kwargs) -> T`
  - `DataclassFactory.batch(cls, size: int, **kwargs) -> list[T]`
- `Use(fn, *args, **kwargs)` class constructor
  - `Use.__init__(self, fn, *args, **kwargs)`
- `ConfigurationException` class constructor

## Required Behavior

- A `DataclassFactory` subclass for a dataclass model builds instances of that model, filling undeclared fields with generated values of the annotated types, including nested dataclass fields.
- `build(**overrides)` uses the provided keyword values instead of generated ones for those fields.
- A factory class attribute assigned `Use(callable)` supplies that callable's return value for the matching model field.
- `batch(n, **overrides)` returns `n` instances; a `Use`/`Require`/`Ignore` factory field whose name is not a model field raises `ConfigurationException` when the factory class is created.
- The package exposes `DataclassFactory`, `Use`, and `ConfigurationException` with the callable paths listed in this contract.
- The submitted package source does not import the forbidden upstream package `polyfactory`.

## Constraints

- Forbidden imports: `polyfactory`.
- Do not implement SQLAlchemy factory plugin.
- Do not implement Pydantic ModelFactory.
- Do not implement async persistence.
- Do not implement runtime import of polyfactory.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — A `DataclassFactory` subclass for a dataclass model builds instances of that model, filling undeclared fields with generated values of the annotated types, including nested dataclass fields.
- **B002** — `build(**overrides)` uses the provided keyword values instead of generated ones for those fields.
- **B003** — A factory class attribute assigned `Use(callable)` supplies that callable's return value for the matching model field.
- **B004** — `batch(n, **overrides)` returns `n` instances; a `Use`/`Require`/`Ignore` factory field whose name is not a model field raises `ConfigurationException` when the factory class is created.
- **B005** — The package exposes `DataclassFactory`, `Use`, and `ConfigurationException` with the callable paths listed in this contract.
- **B006** — The submitted package source does not import the forbidden upstream package `polyfactory`.
<!-- featureliftbench:behavior-clauses:end -->
