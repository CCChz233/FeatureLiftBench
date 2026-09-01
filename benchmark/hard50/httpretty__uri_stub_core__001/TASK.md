# FeatureLift Task: In-process URI stubs

Build a standalone `featurelifted` package providing HTTPretty-style `enable`, `register_uri`, and `last_request` so HTTP clients are stubbed in-process without outbound network access.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    disable,
    enable,
    GET,
    last_request,
    register_uri,
    reset,
)
```

## Required API Details

- `enable(allow_net_connect=True, verbose=False)`
- `disable()`
- `reset()`
- `register_uri(method, uri, body=..., adding_headers=None, forcing_headers=None, status=200, ...)`
- `last_request()`
- `GET` constant must exist

## Required Behavior

- After `enable(allow_net_connect=False)` and `register_uri(GET, url, body=...)`, `urllib.request.urlopen(url)` returns that body with HTTP status 200.
- `last_request()` after a stubbed GET exposes the intercepted request `path`, `method`, and `host` for that URI.
- A stubbed GET whose URI includes `?q=...` records `last_request().querystring` as a mapping from that query key to a one-element list of the value.
- Calling `reset()` while still enabled unregisters previously registered URIs so a later `urlopen` for that URI raises instead of returning the old stub body.
- The package exposes `enable`, `disable`, `reset`, `register_uri`, `last_request`, and `GET` as listed in this contract.
- The submitted package source does not import the forbidden upstream package `httpretty`.

## Constraints

- Forbidden imports: `httpretty`.
- Do not implement real sockets.
- Do not implement http2.
- Do not implement outbound HTTP.
- Do not implement runtime import of httpretty.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — After `enable(allow_net_connect=False)` and `register_uri(GET, url, body=...)`, `urllib.request.urlopen(url)` returns that body with HTTP status 200.
- **B002** — `last_request()` after a stubbed GET exposes the intercepted request `path`, `method`, and `host` for that URI.
- **B003** — A stubbed GET whose URI includes `?q=...` records `last_request().querystring` as a mapping from that query key to a one-element list of the value.
- **B004** — Calling `reset()` while still enabled unregisters previously registered URIs so a later `urlopen` for that URI raises instead of returning the old stub body.
- **B005** — The package exposes `enable`, `disable`, `reset`, `register_uri`, `last_request`, and `GET` as listed in this contract.
- **B006** — The submitted package source does not import the forbidden upstream package `httpretty`.
<!-- featureliftbench:behavior-clauses:end -->
