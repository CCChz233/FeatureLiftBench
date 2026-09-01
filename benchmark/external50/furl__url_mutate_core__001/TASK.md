# FeatureLift Task: furl url mutate

Extract a task-scoped subset of `furl` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    furl,
    Path,
)
```

## Required API Details

- `furl(url: str = '')` class constructor
  - `furl.url` attribute must exist on instances
  - `furl.path` attribute must exist on instances
  - `furl.args` attribute must exist on instances
  - `furl.scheme` attribute must exist on instances
  - `furl.host` attribute must exist on instances
  - `furl.port` attribute must exist on instances
  - `furl.fragment` attribute must exist on instances
- `Path` class must be importable
  - `Path.segments` attribute must exist on instances

## Required Behavior

- furl parses a URL into mutable path segments, query arguments, scheme, host, port, and fragment; mutating any of those components is reflected in the serialized url string.
- Query arguments support mapping assignment and deletion: assigned keys appear in url and deleted keys no longer appear.
- The package exposes furl with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: furl.

## Constraints

- Forbidden imports: `furl`.
- Do not implement network fetch.
- Do not implement original furl import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — furl parses a URL into mutable path segments, query arguments, scheme, host, port, and fragment; mutating any of those components is reflected in the serialized url string.
- **B002** — Query arguments support mapping assignment and deletion: assigned keys appear in url and deleted keys no longer appear.
- **B003** — The package exposes furl with the kinds listed in this contract.
- **B004** — the submitted package does not import forbidden upstream packages: furl.
<!-- featureliftbench:behavior-clauses:end -->
