# FeatureLift Task: Graphene schema execution

Build a standalone `featurelifted` package providing Graphene-style `ObjectType` definitions and `Schema.execute` for queries.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    Field,
    Int,
    ObjectType,
    Schema,
    String,
)
```

## Required API Details

- `ObjectType` class must be importable
- `Schema(query=None, mutation=None, subscription=None, types=None, directives=None, auto_camelcase=True)` class constructor
  - `Schema.__init__(self, query=None, mutation=None, subscription=None, types=None, directives=None, auto_camelcase=True)`
  - `Schema.execute(self, *args, **kwargs)`
- `String` class must be importable
- `Int` class must be importable
- `Field(type_, args=None, resolver=None, source=None, deprecation_reason=None, name=None, description=None, required=False, default_value=None, **extra_args)` class constructor
  - `Field.__init__(self, type_, args=None, resolver=None, source=None, deprecation_reason=None, name=None, description=None, required=False, default_value=None, **extra_args)`

## Required Behavior

- A `Schema` constructed with a query `ObjectType` executes a GraphQL operation string; a field resolver that takes an argument declared as `String(name=String(default_value=...))` uses that default when the argument is omitted and the provided value when it is present.
- A query field declared with `Field(NestedType)` returns nested selected scalars from an `ObjectType` instance returned by the resolver.
- By default `Schema(auto_camelcase=True)` exposes a snake_case Python field such as `hello_world` as the GraphQL field `helloWorld`; querying the snake_case name fails with errors and `data is None`.
- Executing a query for a field that is not on the query type yields `data is None` and a non-empty `errors` collection.
- The package exposes `ObjectType`, `Schema`, `Schema.execute`, `String`, `Int`, and `Field` with the callable paths listed in this contract.
- The submitted package source does not import the forbidden upstream package `graphene`.

## Constraints

- Forbidden imports: `graphene`.
- Do not implement Django integration.
- Do not implement Relay connections and mutations.
- Do not implement async execute.
- Do not implement runtime import of graphene.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — A `Schema` constructed with a query `ObjectType` executes a GraphQL operation string; a field resolver that takes an argument declared as `String(name=String(default_value=...))` uses that default when the argument is omitted and the provided value when it is present.
- **B002** — A query field declared with `Field(NestedType)` returns nested selected scalars from an `ObjectType` instance returned by the resolver.
- **B003** — By default `Schema(auto_camelcase=True)` exposes a snake_case Python field such as `hello_world` as the GraphQL field `helloWorld`; querying the snake_case name fails with errors and `data is None`.
- **B004** — Executing a query for a field that is not on the query type yields `data is None` and a non-empty `errors` collection.
- **B005** — The package exposes `ObjectType`, `Schema`, `Schema.execute`, `String`, `Int`, and `Field` with the callable paths listed in this contract.
- **B006** — The submitted package source does not import the forbidden upstream package `graphene`.
<!-- featureliftbench:behavior-clauses:end -->
