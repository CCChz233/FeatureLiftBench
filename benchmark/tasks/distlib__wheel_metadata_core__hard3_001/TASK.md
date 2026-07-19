# FeatureLift Task: Resource finder and wheel RECORD path normalization

Extract wheel RECORD parsing helpers into `featurelifted`.

## Target API

```python
from featurelifted import to_posix, normalize_record_path, parse_record, validate_record_hash
```

## Required Behavior

- `to_posix` normalizes platform separators to forward slashes.
- `normalize_record_path` applies posix normalization and strips `./` prefixes.
- `parse_record` parses CSV RECORD rows into `(path, digest, size)` tuples.
- `validate_record_hash` validates `sha256=` digests.

## Constraints

- Forbidden imports: `distlib`.
- No installer or locator runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — RECORD parsing
- **B002** — path normalization
- **B003** — hash validation
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: distlib
<!-- featureliftbench:behavior-clauses:end -->
