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

- The extracted feature must support this observable behavior: split/unsplit with SplitResult fields scheme/authority/path/query/fragment. Required observable cases include urisplit fields; split relative ref.
- The extracted feature must support this observable behavior: join absolute and relative refs. Required observable cases include urijoin relative; urijoin strict absolute ref.
- The extracted feature must support this observable behavior: adapted urinorm path/scheme normalization. Required observable cases include urinorm path dots; urinorm scheme case.
- The extracted feature must support this observable behavior: utf-8 percent encode/decode. Required observable cases include encode decode roundtrip.
- The package exposes the required task API paths `featurelifted.urisplit`, `featurelifted.uriunsplit`, `featurelifted.urijoin`, `featurelifted.urinorm`, `featurelifted.uriencode`, `featurelifted.uridecode`, `featurelifted.SplitResult` with the kinds and callable signatures listed in this contract.
- the submitted package does not import forbidden upstream packages: uritools.

## Constraints

- Forbidden imports: `uritools`.
- Do not implement network fetch.
- Do not implement uridefrag/uricompose outside Required API.
- Do not implement original uritools import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: split/unsplit with SplitResult fields scheme/authority/path/query/fragment. Required observable cases include urisplit fields; split relative ref.
- **B002** — The extracted feature must support this observable behavior: join absolute and relative refs. Required observable cases include urijoin relative; urijoin strict absolute ref.
- **B003** — The extracted feature must support this observable behavior: adapted urinorm path/scheme normalization. Required observable cases include urinorm path dots; urinorm scheme case.
- **B004** — The extracted feature must support this observable behavior: utf-8 percent encode/decode. Required observable cases include encode decode roundtrip.
- **B005** — The package exposes the required task API paths `featurelifted.urisplit`, `featurelifted.uriunsplit`, `featurelifted.urijoin`, `featurelifted.urinorm`, `featurelifted.uriencode`, `featurelifted.uridecode`, `featurelifted.SplitResult` with the kinds and callable signatures listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: uritools.
<!-- featureliftbench:behavior-clauses:end -->
