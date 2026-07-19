# FeatureLift Task: version_from_scm

Extract setuptools_scm version normalization into `featurelifted`.

## Target API

```python
from featurelifted import version_from_scm
```

## Required Behavior

- `version_from_scm` normalizes tag names, distance-from-tag dev suffixes, and local node suffixes.
- Dirty trees and positive distance append local version segments.

## Constraints

- Forbidden imports: `setuptools_scm`.
- Use fake SCM inputs; no subprocess git.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — SCM-like version normalization
- **B002** — dev distance suffix
- **B003** — local node suffix
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: setuptools_scm
<!-- featureliftbench:behavior-clauses:end -->
