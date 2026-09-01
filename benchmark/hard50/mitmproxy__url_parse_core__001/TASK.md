# FeatureLift Task: URL parse

Build a standalone `featurelifted` package that parses URLs like mitmproxy `parse`/`unparse`, returning `(scheme, host, port, path)` bytes and reconstructing the URL, without running a proxy.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    parse,
    unparse,
)
```

## Required API Details

- `parse(url: str | bytes) -> tuple[bytes, bytes, int, bytes]`
- `unparse(scheme, host, port, path)`

## Required Behavior

- `parse("https://example.com/foo")` returns `(b"https", b"example.com", 443, b"/foo")`; `parse("https://example.org/path")` returns `(b"https", b"example.org", 443, b"/path")`.
- `unparse(*parse("https://example.com/bar"))` equals `b"https://example.com/bar"`.
- `parse("http://127.0.0.1:8080/x")` returns `(b"http", b"127.0.0.1", 8080, b"/x")`.
- `parse("not-a-url")` raises `ValueError`.
- The package exposes `parse` and `unparse`.
- The submitted package source does not import the forbidden upstream package `mitmproxy`.

## Constraints

- Forbidden imports: `mitmproxy`.
- Do not implement proxy listen.
- Do not implement addons.
- Do not implement network.
- Do not implement runtime import of mitmproxy.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — `parse("https://example.com/foo")` returns `(b"https", b"example.com", 443, b"/foo")`; `parse("https://example.org/path")` returns `(b"https", b"example.org", 443, b"/path")`.
- **B002** — `unparse(*parse("https://example.com/bar"))` equals `b"https://example.com/bar"`.
- **B003** — `parse("http://127.0.0.1:8080/x")` returns `(b"http", b"127.0.0.1", 8080, b"/x")`.
- **B004** — `parse("not-a-url")` raises `ValueError`.
- **B005** — The package exposes `parse` and `unparse`.
- **B006** — The submitted package source does not import the forbidden upstream package `mitmproxy`.
<!-- featureliftbench:behavior-clauses:end -->
