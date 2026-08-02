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

- `PackageURL` class must be importable
  - `PackageURL.from_string` callable must exist
  - `PackageURL.to_string` callable must exist
  - `PackageURL.type` attribute must exist on instances
  - `PackageURL.name` attribute must exist on instances
  - `PackageURL.namespace` attribute must exist on instances
  - `PackageURL.version` attribute must exist on instances
- `PackageURL.from_string` callable must exist
- `PackageURL.to_string` callable must exist

## Required Behavior

- The extracted feature must support this observable behavior: from_string exposes type/namespace/name/version. Required observable cases include from string fields; constructor.
- The extracted feature must support this observable behavior: to_string roundtrips canonical purls. Required observable cases include to string roundtrip; qualifiers normalize.
- The extracted feature must support this observable behavior: invalid purls raise ValueError. Required observable cases include invalid purl.
- Qualifiers are serialized in stable order.
- The package exposes PackageURL.from_string/to_string with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: packageurl.

## Constraints

- Forbidden imports: `packageurl`.
- Do not implement ecosystem network lookups.
- Do not implement original packageurl import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: from_string exposes type/namespace/name/version. Required observable cases include from string fields; constructor.
- **B002** — The extracted feature must support this observable behavior: to_string roundtrips canonical purls. Required observable cases include to string roundtrip; qualifiers normalize.
- **B003** — The extracted feature must support this observable behavior: invalid purls raise ValueError. Required observable cases include invalid purl.
- **B004** — Qualifiers are serialized in stable order.
- **B005** — The package exposes PackageURL.from_string/to_string with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: packageurl.
<!-- featureliftbench:behavior-clauses:end -->
