# FeatureLift Task: URI split/join/normalize helpers

Extract a task-scoped subset of `uritools` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    SplitResult,
    uridecode,
    uriencode,
    urijoin,
    urinorm,
    urisplit,
    uriunsplit,
)
```

## Required API Details

- `urisplit(uri: str) -> SplitResult`
- `uriunsplit(parts: SplitResult | tuple) -> str`
- `urijoin(base: str, ref: str, strict: bool = False) -> str`
- `urinorm(uri: str) -> str`
- `uriencode(s: str, safe: str = '', encoding: str = 'utf-8') -> str`
- `uridecode(s: str, encoding: str = 'utf-8') -> str`
- `SplitResult` class must be importable

## Required Behavior

- urisplit returns a SplitResult exposing `scheme`, `authority`, `path`, `query`, and `fragment`; uriunsplit reconstructs the original absolute URI, while splitting a relative path leaves its scheme empty and preserves the path.
- urijoin resolves `../b` against `https://example.com/a/` as `https://example.com/b`, and with `strict=True` an absolute reference replaces the base URI unchanged.
- urinorm removes `.` and `..` path segments and lowercases an uppercase URI scheme, so normalized output for an HTTP URI contains the collapsed path and begins with `http://`.
- uriencode percent-encodes non-ASCII UTF-8 text, producing text or ASCII bytes containing `%`, and uridecode accepts that result and restores the original Unicode string.
- The package exposes the required task API paths `featurelifted.urisplit`, `featurelifted.uriunsplit`, `featurelifted.urijoin`, `featurelifted.urinorm`, `featurelifted.uriencode`, `featurelifted.uridecode`, `featurelifted.SplitResult` with the kinds and callable signatures listed in this contract.
- Scanning every Python file in the submitted package finds no `import uritools` or `from uritools ...` statement.

## Constraints

- Forbidden imports: `uritools`.
- Do not implement network fetch.
- Do not implement uridefrag/uricompose outside Required API.
- Do not implement original uritools import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — urisplit returns a SplitResult exposing `scheme`, `authority`, `path`, `query`, and `fragment`; uriunsplit reconstructs the original absolute URI, while splitting a relative path leaves its scheme empty and preserves the path.
- **B002** — urijoin resolves `../b` against `https://example.com/a/` as `https://example.com/b`, and with `strict=True` an absolute reference replaces the base URI unchanged.
- **B003** — urinorm removes `.` and `..` path segments and lowercases an uppercase URI scheme, so normalized output for an HTTP URI contains the collapsed path and begins with `http://`.
- **B004** — uriencode percent-encodes non-ASCII UTF-8 text, producing text or ASCII bytes containing `%`, and uridecode accepts that result and restores the original Unicode string.
- **B005** — The package exposes the required task API paths `featurelifted.urisplit`, `featurelifted.uriunsplit`, `featurelifted.urijoin`, `featurelifted.urinorm`, `featurelifted.uriencode`, `featurelifted.uridecode`, `featurelifted.SplitResult` with the kinds and callable signatures listed in this contract.
- **B006** — Scanning every Python file in the submitted package finds no `import uritools` or `from uritools ...` statement.
<!-- featureliftbench:behavior-clauses:end -->
