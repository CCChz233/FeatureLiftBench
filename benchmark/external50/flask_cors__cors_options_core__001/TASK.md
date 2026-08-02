# FeatureLift Task: flask-cors options

Extract a task-scoped subset of `flask-cors` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    CORS,
    cross_origin,
)
```

## Required API Details

- `CORS(app=None, **options)` class constructor
- `cross_origin(**options)`

## Required Behavior

- The extracted feature must support this observable behavior: CORS(app) reflects Origin on GET responses. Required observable cases include cors app headers.
- The extracted feature must support this observable behavior: cross_origin decorator sets per-route ACAO. Required observable cases include cross origin decorator.
- The extracted feature must support this observable behavior: OPTIONS preflight exposes allowed methods. Required observable cases include options preflight.
- Tests use Flask test client only; Flask is an allowed dependency.
- The package exposes CORS and cross_origin with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: flask_cors.

## Constraints

- Forbidden imports: `flask_cors`.
- Do not implement real browsers.
- Do not implement original flask_cors import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: CORS(app) reflects Origin on GET responses. Required observable cases include cors app headers.
- **B002** — The extracted feature must support this observable behavior: cross_origin decorator sets per-route ACAO. Required observable cases include cross origin decorator.
- **B003** — The extracted feature must support this observable behavior: OPTIONS preflight exposes allowed methods. Required observable cases include options preflight.
- **B004** — Tests use Flask test client only; Flask is an allowed dependency.
- **B005** — The package exposes CORS and cross_origin with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: flask_cors.
<!-- featureliftbench:behavior-clauses:end -->
