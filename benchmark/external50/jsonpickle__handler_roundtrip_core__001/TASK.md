# FeatureLift Task: jsonpickle handler roundtrip

Extract a task-scoped subset of `jsonpickle` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    decode,
    encode,
    handlers,
    register,
)
```

## Required API Details

- `encode(obj, unpicklable: bool = True, make_refs: bool = True) -> str`
- `decode(string: str)`
- `register(cls, handler, base: bool = False) -> None`
- `handlers.BaseHandler` class must be importable

## Required Behavior

- encode and decode round-trip JSON-compatible containers; after register associates a class with a BaseHandler subclass, the handler's flatten and restore methods round-trip instances of that class.
- encode(obj, unpicklable=False) serializes an object's attributes as ordinary JSON data, so decode returns a dictionary snapshot rather than reconstructing the object.
- The package exposes encode/decode/register/BaseHandler with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: jsonpickle.

## Constraints

- Forbidden imports: `jsonpickle`.
- Do not implement numpy/pandas backends.
- Do not implement original jsonpickle import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — encode and decode round-trip JSON-compatible containers; after register associates a class with a BaseHandler subclass, the handler's flatten and restore methods round-trip instances of that class.
- **B002** — encode(obj, unpicklable=False) serializes an object's attributes as ordinary JSON data, so decode returns a dictionary snapshot rather than reconstructing the object.
- **B003** — The package exposes encode/decode/register/BaseHandler with the kinds listed in this contract.
- **B004** — the submitted package does not import forbidden upstream packages: jsonpickle.
<!-- featureliftbench:behavior-clauses:end -->
