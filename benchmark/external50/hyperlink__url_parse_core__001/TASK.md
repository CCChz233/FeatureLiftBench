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
- `URL.from_text` callable must exist
- `URL.replace` callable must exist
- `URL.click` callable must exist
- `URL.to_text` callable must exist
- `URLParseError` must be importable and raisable

## Required Behavior

- The extracted feature must support this observable behavior: URL.from_text and to_text roundtrip fields. Required observable cases include from text and to text; replace scheme host.
- The extracted feature must support this observable behavior: click resolves relative refs. Required observable cases include click relative.
- The extracted feature must support this observable behavior: replace returns new URL without mutating original. Required observable cases include immutable replace.
- URLParseError is raised on malformed authority segments.
- The package exposes URL/URLParseError with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: hyperlink.

## Constraints

- Forbidden imports: `hyperlink`.
- Do not implement network resolve.
- Do not implement original hyperlink import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: URL.from_text and to_text roundtrip fields. Required observable cases include from text and to text; replace scheme host.
- **B002** — The extracted feature must support this observable behavior: click resolves relative refs. Required observable cases include click relative.
- **B003** — The extracted feature must support this observable behavior: replace returns new URL without mutating original. Required observable cases include immutable replace.
- **B004** — URLParseError is raised on malformed authority segments.
- **B005** — The package exposes URL/URLParseError with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: hyperlink.
<!-- featureliftbench:behavior-clauses:end -->
