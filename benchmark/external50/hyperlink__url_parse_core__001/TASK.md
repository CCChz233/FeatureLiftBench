# FeatureLift Task: hyperlink url parse

Extract a task-scoped subset of `hyperlink` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    URL,
    URLParseError,
)
```

## Required API Details

- `URL` class must be importable
- `URL.from_text(text: str) -> URL`
- `URL.replace(scheme=None, host=None, port=None, path=None, query=None, fragment=None, root=None, userinfo=None, uses_netloc=None) -> URL`
- `URL.click(href: str = '') -> URL`
- `URL.to_text(with_password: bool = False) -> str`
- `URLParseError` must be importable and raisable

## Required Behavior

- URL.from_text parses absolute URL text, to_text serializes its components, replace returns a modified URL without mutating the original, and click resolves relative references against the base URL.
- URL.from_text raises URLParseError for malformed authority syntax such as an unterminated bracketed IPv6 host.
- The package exposes URL/URLParseError with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: hyperlink.

## Constraints

- Forbidden imports: `hyperlink`.
- Do not implement network resolve.
- Do not implement original hyperlink import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — URL.from_text parses absolute URL text, to_text serializes its components, replace returns a modified URL without mutating the original, and click resolves relative references against the base URL.
- **B002** — URL.from_text raises URLParseError for malformed authority syntax such as an unterminated bracketed IPv6 host.
- **B003** — The package exposes URL/URLParseError with the kinds listed in this contract.
- **B004** — the submitted package does not import forbidden upstream packages: hyperlink.
<!-- featureliftbench:behavior-clauses:end -->
