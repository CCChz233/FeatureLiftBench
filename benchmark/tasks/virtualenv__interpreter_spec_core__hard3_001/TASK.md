# FeatureLift Task: parse_spec match_version

Extract virtualenv interpreter discovery spec parsing into `featurelifted`.

## Target API

```python
from featurelifted import parse_spec, match_version, discover_paths, InvalidInterpreterSpec
```

## Required Behavior

- `parse_spec` parses version constraints and path globs from interpreter specs.
- `match_version` evaluates constraint operators including `~=`.
- `discover_paths` filters candidate paths by spec.

## Constraints

- Forbidden imports: `virtualenv`.
- No process spawning or environment creation.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — interpreter spec parsing
- **B002** — version matching
- **B003** — path discovery
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: virtualenv
<!-- featureliftbench:behavior-clauses:end -->
