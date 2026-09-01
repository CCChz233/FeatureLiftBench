# FeatureLift Task: toolz compose pipe curry

Extract a task-scoped subset of `toolz` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    compose,
    curry,
    identity,
    pipe,
)
```

## Required API Details

- `compose(*funcs)`
- `pipe(data, *funcs)`
- `curry` class must be importable
- `identity(x)`

## Required Behavior

- `compose` accepts callables and returns a callable that applies them from right to left; `identity` returns its argument unchanged and can participate in a composition.
- `pipe` accepts an initial value followed by callables and returns the result of applying those callables from left to right.
- `curry` wraps a callable so that required positional arguments may be supplied across successive calls or together in one call.
- A curried callable accepts keyword arguments, preserves defaulted parameters, and combines them with positional arguments supplied by a later call.
- The package exposes compose/pipe/curry/identity with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: toolz.

## Constraints

- Forbidden imports: `toolz`.
- Do not implement cytoolz.
- Do not implement parallelism.
- Do not implement original toolz import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — `compose` accepts callables and returns a callable that applies them from right to left; `identity` returns its argument unchanged and can participate in a composition.
- **B002** — `pipe` accepts an initial value followed by callables and returns the result of applying those callables from left to right.
- **B003** — `curry` wraps a callable so that required positional arguments may be supplied across successive calls or together in one call.
- **B004** — A curried callable accepts keyword arguments, preserves defaulted parameters, and combines them with positional arguments supplied by a later call.
- **B005** — The package exposes compose/pipe/curry/identity with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: toolz.
<!-- featureliftbench:behavior-clauses:end -->
