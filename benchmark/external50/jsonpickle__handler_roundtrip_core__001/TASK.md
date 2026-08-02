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

- `encode` callable must exist
- `decode` callable must exist
- `register` callable must exist
- `handlers.BaseHandler` class must be importable

## Required Behavior

- The extracted feature must support this observable behavior: encode/decode roundtrip for dict payloads. Required observable cases include encode decode builtin.
- The extracted feature must support this observable behavior: register BaseHandler restores custom classes. Required observable cases include custom handler roundtrip.
- The extracted feature must support this observable behavior: unpicklable=False yields dict snapshots. Required observable cases include unpicklable false dict mode.
- Handler registry is global; tests register handlers explicitly.
- The package exposes encode/decode/register/BaseHandler with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: jsonpickle.

## Constraints

- Forbidden imports: `jsonpickle`.
- Do not implement numpy/pandas backends.
- Do not implement original jsonpickle import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: encode/decode roundtrip for dict payloads. Required observable cases include encode decode builtin.
- **B002** — The extracted feature must support this observable behavior: register BaseHandler restores custom classes. Required observable cases include custom handler roundtrip.
- **B003** — The extracted feature must support this observable behavior: unpicklable=False yields dict snapshots. Required observable cases include unpicklable false dict mode.
- **B004** — Handler registry is global; tests register handlers explicitly.
- **B005** — The package exposes encode/decode/register/BaseHandler with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: jsonpickle.
<!-- featureliftbench:behavior-clauses:end -->
