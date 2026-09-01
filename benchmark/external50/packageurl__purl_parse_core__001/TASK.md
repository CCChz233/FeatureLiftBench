# FeatureLift Task: packageurl purl parse

Extract a task-scoped subset of `packageurl` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    PackageURL,
)
```

## Required API Details

- `PackageURL(type: str, name: str, namespace: str | None = None, version: str | None = None, qualifiers=None, subpath: str | None = None)` class constructor
  - `PackageURL.from_string(purl: str) -> PackageURL`
  - `PackageURL.to_string() -> str`
  - `PackageURL.type` attribute must exist on instances
  - `PackageURL.name` attribute must exist on instances
  - `PackageURL.namespace` attribute must exist on instances
  - `PackageURL.version` attribute must exist on instances

## Required Behavior

- PackageURL.from_string parses type, namespace, name, and version fields; constructing the same fields directly and calling to_string produces canonical `pkg:` text, with qualifiers retained in stable order.
- PackageURL.from_string raises ValueError when the input is not a valid `pkg:` URL.
- The package exposes PackageURL.from_string/to_string with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: packageurl.

## Constraints

- Forbidden imports: `packageurl`.
- Do not implement ecosystem network lookups.
- Do not implement original packageurl import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — PackageURL.from_string parses type, namespace, name, and version fields; constructing the same fields directly and calling to_string produces canonical `pkg:` text, with qualifiers retained in stable order.
- **B002** — PackageURL.from_string raises ValueError when the input is not a valid `pkg:` URL.
- **B003** — The package exposes PackageURL.from_string/to_string with the kinds listed in this contract.
- **B004** — the submitted package does not import forbidden upstream packages: packageurl.
<!-- featureliftbench:behavior-clauses:end -->
