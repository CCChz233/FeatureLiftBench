# FeatureLift Task: FST parse and mutate

Build a standalone `featurelifted` package providing RedBaron-style FST parse, `find`, rename, and `dumps` roundtrip for Python source.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    RedBaron,
)
```

## Required API Details

- `RedBaron(source_code)` class constructor
  - `RedBaron.__init__(self, source_code)`
  - `RedBaron.find(self, identifier, *args, **kwargs)`
  - `RedBaron.dumps(self)`

## Required Behavior

- Constructing `RedBaron(source)` and calling `dumps()` returns source that is identical to the original input, including indentation and trailing newline.
- `find("def", name=...)` locates that function; assigning a new `.name` and calling `dumps()` emits the renamed `def` line while leaving the function body formatting unchanged.
- The package exposes `RedBaron` with construction, `find`, and `dumps` as listed in this contract.
- The submitted package source does not import the forbidden upstream package `redbaron`.

## Constraints

- Forbidden imports: `redbaron`.
- Do not implement baron internals dump formats unused.
- Do not implement ipython/notebook helpers.
- Do not implement runtime import of redbaron.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — Constructing `RedBaron(source)` and calling `dumps()` returns source that is identical to the original input, including indentation and trailing newline.
- **B002** — `find("def", name=...)` locates that function; assigning a new `.name` and calling `dumps()` emits the renamed `def` line while leaving the function body formatting unchanged.
- **B003** — The package exposes `RedBaron` with construction, `find`, and `dumps` as listed in this contract.
- **B004** — The submitted package source does not import the forbidden upstream package `redbaron`.
<!-- featureliftbench:behavior-clauses:end -->
