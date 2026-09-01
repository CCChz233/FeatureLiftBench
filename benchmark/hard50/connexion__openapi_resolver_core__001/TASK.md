# FeatureLift Task: OpenAPI operationId resolver

Build a standalone `featurelifted` package that resolves OpenAPI operations to Python view functions from in-memory spec dictionaries, without live HTTP.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    Resolution,
    Resolver,
    ResolverError,
    RestyResolver,
)
```

## Required API Details

- `Resolver(function_resolver: Callable = get_function_from_name)` class constructor
  - `Resolver.__init__(self, function_resolver: Callable = get_function_from_name)`
  - `Resolver.resolve(self, operation)`
  - `Resolver.resolve_operation_id(self, operation)`
- `RestyResolver(default_module_name: str, *, collection_endpoint_name: str = 'search')` class constructor
  - `RestyResolver.__init__(self, default_module_name: str, *, collection_endpoint_name: str = 'search')`
  - `RestyResolver.resolve_operation_id(self, operation)`
- `Resolution(function, operation_id)` class constructor
  - `Resolution.__init__(self, function, operation_id)`
- `ResolverError` must be importable and raisable

## Required Behavior

- When `Resolver.resolve` is given an operation whose `operation_id` is a dotted import path taken from an in-memory OpenAPI path item, it returns a `Resolution` whose `function` is that imported callable and whose `operation_id` matches the spec.
- When `RestyResolver.resolve_operation_id` is given an operation with no `operation_id`, a collection GET such as `/pets` resolves to `{module}.pets.search`, while an item path whose last component is a template variable uses the HTTP method name instead of `search`.
- When `RestyResolver.resolve_operation_id` is given an operation that already has an `operation_id`, that explicit id is returned instead of a REST-semantic id derived from the path.
- When `Resolver.resolve` is given an `operation_id` that cannot be imported as a Python object, it raises `ResolverError`.
- The package exposes `Resolver`, `RestyResolver`, `Resolution`, and `ResolverError` with the callable signatures listed in this contract.
- The submitted package source does not import the forbidden upstream package `connexion`.

## Constraints

- Forbidden imports: `connexion`.
- Do not implement live HTTP servers.
- Do not implement urllib.Request / remote spec fetch.
- Do not implement Flask/Starlette app hosting.
- Do not implement runtime import of connexion.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — When `Resolver.resolve` is given an operation whose `operation_id` is a dotted import path taken from an in-memory OpenAPI path item, it returns a `Resolution` whose `function` is that imported callable and whose `operation_id` matches the spec.
- **B002** — When `RestyResolver.resolve_operation_id` is given an operation with no `operation_id`, a collection GET such as `/pets` resolves to `{module}.pets.search`, while an item path whose last component is a template variable uses the HTTP method name instead of `search`.
- **B003** — When `RestyResolver.resolve_operation_id` is given an operation that already has an `operation_id`, that explicit id is returned instead of a REST-semantic id derived from the path.
- **B004** — When `Resolver.resolve` is given an `operation_id` that cannot be imported as a Python object, it raises `ResolverError`.
- **B005** — The package exposes `Resolver`, `RestyResolver`, `Resolution`, and `ResolverError` with the callable signatures listed in this contract.
- **B006** — The submitted package source does not import the forbidden upstream package `connexion`.
<!-- featureliftbench:behavior-clauses:end -->
