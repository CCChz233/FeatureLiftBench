# FeatureLift Task: HTTP header parse

Build a standalone `featurelifted` package that parses HTTP header blocks like Tornado `HTTPHeaders`, including duplicate `Set-Cookie` values and malformed-line errors, without running an IOLoop or HTTP server.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    HTTPHeaders,
    HTTPInputError,
)
```

## Required API Details

- `HTTPHeaders()` class constructor
  - `HTTPHeaders.parse(cls, headers: str)`
  - `HTTPHeaders.add(self, name: str, value: str)`
  - `HTTPHeaders.get_list(self, name: str)`
- `HTTPInputError` class constructor

## Required Behavior

- `HTTPHeaders.parse` of a CRLF-separated block such as `Content-Type: text/html` / `Content-Length: 42` or `Accept: text/plain` / `Host: example.com` stores those header values.
- Two `add("Set-Cookie", ...)` calls make `get_list("set-cookie")` return both values, and the combined mapping value is comma-joined.
- Parsed header names are HTTP-cased (`content-type` becomes `Content-Type`) and lookup is case-insensitive.
- `HTTPHeaders.parse` on a line with no colon raises `HTTPInputError`.
- The package exposes `HTTPHeaders` with `parse`, `add`, and `get_list`, plus `HTTPInputError`.
- The submitted package source does not import the forbidden upstream package `tornado`.

## Constraints

- Forbidden imports: `tornado`.
- Do not implement IOLoop.
- Do not implement HTTPServer.
- Do not implement network.
- Do not implement runtime import of tornado.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — `HTTPHeaders.parse` of a CRLF-separated block such as `Content-Type: text/html` / `Content-Length: 42` or `Accept: text/plain` / `Host: example.com` stores those header values.
- **B002** — Two `add("Set-Cookie", ...)` calls make `get_list("set-cookie")` return both values, and the combined mapping value is comma-joined.
- **B003** — Parsed header names are HTTP-cased (`content-type` becomes `Content-Type`) and lookup is case-insensitive.
- **B004** — `HTTPHeaders.parse` on a line with no colon raises `HTTPInputError`.
- **B005** — The package exposes `HTTPHeaders` with `parse`, `add`, and `get_list`, plus `HTTPInputError`.
- **B006** — The submitted package source does not import the forbidden upstream package `tornado`.
<!-- featureliftbench:behavior-clauses:end -->
