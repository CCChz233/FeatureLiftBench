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

- The extracted feature must support this observable behavior: parse and mutate path/query. Required observable cases include parse and mutate path; query args.
- The extracted feature must support this observable behavior: scheme/host/port/fragment mutation. Required observable cases include set scheme host; fragment and port.
- The extracted feature must support this observable behavior: remove query keys. Required observable cases include remove query key.
- furl.url returns the serialized URL string.
- The package exposes furl with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: furl.

## Constraints

- Forbidden imports: `furl`.
- Do not implement network fetch.
- Do not implement original furl import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: parse and mutate path/query. Required observable cases include parse and mutate path; query args.
- **B002** — The extracted feature must support this observable behavior: scheme/host/port/fragment mutation. Required observable cases include set scheme host; fragment and port.
- **B003** — The extracted feature must support this observable behavior: remove query keys. Required observable cases include remove query key.
- **B004** — furl.url returns the serialized URL string.
- **B005** — The package exposes furl with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: furl.
<!-- featureliftbench:behavior-clauses:end -->
