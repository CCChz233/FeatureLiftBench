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

- CORS(app, ...) installs Flask response handling that permits configured origins on ordinary requests and emits Access-Control-Allow-Methods for valid OPTIONS preflight requests.
- cross_origin(**options) returns a route decorator; when configured with an allowed origin, the decorated response carries that origin in Access-Control-Allow-Origin.
- The package exposes CORS and cross_origin with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: flask_cors.

## Constraints

- Forbidden imports: `flask_cors`.
- Do not implement real browsers.
- Do not implement original flask_cors import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — CORS(app, ...) installs Flask response handling that permits configured origins on ordinary requests and emits Access-Control-Allow-Methods for valid OPTIONS preflight requests.
- **B002** — cross_origin(**options) returns a route decorator; when configured with an allowed origin, the decorated response carries that origin in Access-Control-Allow-Origin.
- **B003** — The package exposes CORS and cross_origin with the kinds listed in this contract.
- **B004** — the submitted package does not import forbidden upstream packages: flask_cors.
<!-- featureliftbench:behavior-clauses:end -->
