# FeatureLift Task: URLMap prefix dispatch

Build a standalone `featurelifted` package providing Paste-style `URLMap` prefix dispatch for WSGI applications.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    URLMap,
)
```

## Required API Details

- `URLMap(not_found_app=None)` class constructor
  - `URLMap.__init__(self, not_found_app=None)`
  - `URLMap.__setitem__(self, url, app) -> None`
  - `URLMap.__getitem__(self, url)`
  - `URLMap.__call__(self, environ, start_response)`

## Required Behavior

- Assigning a WSGI application to `URLMap[prefix]` dispatches requests whose `PATH_INFO` equals that prefix: the application is called, `SCRIPT_NAME` gains the prefix, and `PATH_INFO` becomes empty.
- When both a shorter prefix and a longer prefix are mounted, the longest matching prefix is selected; a path that continues past the shorter prefix but does not match the longer one still uses the shorter prefix and forwards the remainder in `PATH_INFO`.
- A request whose `PATH_INFO` matches no mounted prefix is answered with an HTTP 404 status.
- A mount key of the form `http://host/path` only matches that HTTP host; the same path on another host is not found, while host-less prefixes still match any host.
- The package exposes `URLMap` with construction, `__setitem__`, `__getitem__`, and WSGI `__call__` as listed in this contract.
- The submitted package source does not import the forbidden upstream package `paste`.

## Constraints

- Forbidden imports: `paste`.
- Do not implement HTTP server sockets.
- Do not implement Paste Deploy config factories.
- Do not implement HTTPS/proxy applications.
- Do not implement runtime import of paste.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — Assigning a WSGI application to `URLMap[prefix]` dispatches requests whose `PATH_INFO` equals that prefix: the application is called, `SCRIPT_NAME` gains the prefix, and `PATH_INFO` becomes empty.
- **B002** — When both a shorter prefix and a longer prefix are mounted, the longest matching prefix is selected; a path that continues past the shorter prefix but does not match the longer one still uses the shorter prefix and forwards the remainder in `PATH_INFO`.
- **B003** — A request whose `PATH_INFO` matches no mounted prefix is answered with an HTTP 404 status.
- **B004** — A mount key of the form `http://host/path` only matches that HTTP host; the same path on another host is not found, while host-less prefixes still match any host.
- **B005** — The package exposes `URLMap` with construction, `__setitem__`, `__getitem__`, and WSGI `__call__` as listed in this contract.
- **B006** — The submitted package source does not import the forbidden upstream package `paste`.
<!-- featureliftbench:behavior-clauses:end -->
