# FeatureLift Task: Decorator registry and scanner dispatch

Extract callback attachment, category filtering, and module scanning into a deterministic plugin-dispatch workflow.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    attach,
    AttachInfo,
    lift,
    Scanner,
)
```

## Required API Details

- `attach(wrapped, callback, category=None, depth=1, name=None) -> AttachInfo`
- `Scanner(**context)` class constructor
  - `Scanner.scan(package, categories=None, onerror=None, ignore=None) -> None`
- `AttachInfo` class must be importable
- `lift` class must be importable

## Required Behavior

- attach records a callback on a function or class without replacing the wrapped object.
- Scanner.scan discovers attached objects in a module and dispatches callbacks with scanner context, name, and object.
- Category filters select only matching registrations while preserving deterministic callback order.
- The submitted package does not import venusian or scan the network or unrelated filesystem paths.

## Constraints

- Forbidden imports: `venusian`.
- Do not implement filesystem package walks in evaluator cases.
- Do not implement zip imports.
- Do not implement namespace package edge cases.
- Do not implement original venusian import at runtime.

## Public vs Hidden Tests

Public tests cover common use. Hidden tests cover documented edge, configuration, state, API-surface, and isolation behavior only.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — attach records a callback on a function or class without replacing the wrapped object.
- **B002** — Scanner.scan discovers attached objects in a module and dispatches callbacks with scanner context, name, and object.
- **B003** — Category filters select only matching registrations while preserving deterministic callback order.
- **B004** — The submitted package does not import venusian or scan the network or unrelated filesystem paths.
<!-- featureliftbench:behavior-clauses:end -->
