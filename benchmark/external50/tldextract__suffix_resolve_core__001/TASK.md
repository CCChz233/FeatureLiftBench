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
  - `TLDExtract.__call__(self, url: str)`
- `extract(url: str)`
- `ExtractResult` class must be importable
  - `ExtractResult.subdomain` attribute must exist on instances
  - `ExtractResult.domain` attribute must exist on instances
  - `ExtractResult.suffix` attribute must exist on instances

## Required Behavior

- TLDExtract(suffix_list_urls=()) splits a URL into subdomain, domain, and public suffix fields, including multi-label suffixes such as co.uk.
- Extracting a bare host such as example.com returns an empty subdomain, domain `example`, and suffix `com`; the module-level extract(url) convenience function returns the same ExtractResult shape.
- For https://foo.bar.co.uk, joining ExtractResult.domain and ExtractResult.suffix yields the registered domain bar.co.uk.
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

- **B001** — TLDExtract(suffix_list_urls=()) splits a URL into subdomain, domain, and public suffix fields, including multi-label suffixes such as co.uk.
- **B002** — Extracting a bare host such as example.com returns an empty subdomain, domain `example`, and suffix `com`; the module-level extract(url) convenience function returns the same ExtractResult shape.
- **B003** — For https://foo.bar.co.uk, joining ExtractResult.domain and ExtractResult.suffix yields the registered domain bar.co.uk.
- **B004** — suffix_list_urls=() disables network suffix fetch.
- **B005** — The package exposes TLDExtract/extract/ExtractResult with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: tldextract.
<!-- featureliftbench:behavior-clauses:end -->
