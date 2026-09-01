# FeatureLift Task: Mapper match and generate

Build a standalone `featurelifted` package providing Routes-style `Mapper` connect, match, and generate.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    Mapper,
)
```

## Required API Details

- `Mapper(controller_scan=None, directory=None, always_scan=False, register=True, explicit=True)` class constructor
  - `Mapper.__init__(self, controller_scan=None, directory=None, always_scan=False, register=True, explicit=True)`
  - `Mapper.connect(self, *args, **kargs)`
  - `Mapper.match(self, url=None, environ=None)`
  - `Mapper.generate(self, *args, **kargs)`

## Required Behavior

- After `connect` registers a literal path with controller and action, `match` of that path returns a dict containing those values.
- A connected template such as `/user/{id}` captures the path segment into the match dict.
- A URL that matches no connected route causes `match` to return `None`.
- `generate` with the connected controller/action (and template variables) rebuilds the original path.
- The package exposes `Mapper` with construction, `connect`, `match`, and `generate` as listed in this contract.
- The submitted package source does not import the forbidden upstream package `routes`.

## Constraints

- Forbidden imports: `routes`.
- Do not implement WSGI middleware serving.
- Do not implement HTTP servers.
- Do not implement runtime import of routes.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — After `connect` registers a literal path with controller and action, `match` of that path returns a dict containing those values.
- **B002** — A connected template such as `/user/{id}` captures the path segment into the match dict.
- **B003** — A URL that matches no connected route causes `match` to return `None`.
- **B004** — `generate` with the connected controller/action (and template variables) rebuilds the original path.
- **B005** — The package exposes `Mapper` with construction, `connect`, `match`, and `generate` as listed in this contract.
- **B006** — The submitted package source does not import the forbidden upstream package `routes`.
<!-- featureliftbench:behavior-clauses:end -->
