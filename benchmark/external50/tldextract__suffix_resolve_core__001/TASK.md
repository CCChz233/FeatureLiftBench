# FeatureLift Task: tldextract suffix resolve

Extract a task-scoped subset of `tldextract` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    extract,
    ExtractResult,
    TLDExtract,
)
```

## Required API Details

- `TLDExtract` class must be importable
  - `TLDExtract.__call__` callable must exist
- `extract` callable must exist
- `ExtractResult` class must be importable
  - `ExtractResult.subdomain` attribute must exist on instances
  - `ExtractResult.domain` attribute must exist on instances
  - `ExtractResult.suffix` attribute must exist on instances

## Required Behavior

- The extracted feature must support this observable behavior: offline TLDExtract splits URLs. Required observable cases include tldextract offline.
- The extracted feature must support this observable behavior: extract convenience helper. Required observable cases include extract convenience.
- The extracted feature must support this observable behavior: registered domain and bare hosts. Required observable cases include registered domain; no subdomain.
- suffix_list_urls=() disables network suffix fetch.
- The package exposes TLDExtract/extract/ExtractResult with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: tldextract.

## Constraints

- Forbidden imports: `tldextract`.
- Do not implement live PSL download.
- Do not implement original tldextract import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: offline TLDExtract splits URLs. Required observable cases include tldextract offline.
- **B002** — The extracted feature must support this observable behavior: extract convenience helper. Required observable cases include extract convenience.
- **B003** — The extracted feature must support this observable behavior: registered domain and bare hosts. Required observable cases include registered domain; no subdomain.
- **B004** — suffix_list_urls=() disables network suffix fetch.
- **B005** — The package exposes TLDExtract/extract/ExtractResult with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: tldextract.
<!-- featureliftbench:behavior-clauses:end -->
