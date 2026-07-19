# FeatureLift Task: build_url normalize_headers

Extract aiohttp URL/header helpers into `featurelifted`.

## Target API

```python
from featurelifted import build_url, normalize_headers, CIMultiDict, InvalidHeaderName
```

## Required Behavior

- `build_url` merges query parameters into a base URL.
- `normalize_headers` returns a case-insensitive `CIMultiDict`.
- Invalid header names raise `InvalidHeaderName`.

## Constraints

- Forbidden imports: `aiohttp`.
- No client/server or async runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — URL query merging
- **B002** — CIMultiDict headers
- **B003** — header validation
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: aiohttp
<!-- featureliftbench:behavior-clauses:end -->
