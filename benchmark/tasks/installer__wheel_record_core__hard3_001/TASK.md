# FeatureLift Task: parse_wheel_record find_dist_info

Extract installer wheel RECORD helpers into `featurelifted`.

## Target API

```python
from featurelifted import parse_wheel_record, find_dist_info, script_name
```

## Required Behavior

- `parse_wheel_record` parses CSV RECORD rows into `(path, digest, size)` tuples.
- `find_dist_info` locates a unique `.dist-info` directory among archive names.
- `script_name` derives console script names from entry point targets.

## Constraints

- Forbidden imports: `installer`.
- No actual install to system paths.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — RECORD CSV parsing
- **B002** — dist-info discovery
- **B003** — script name extraction
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: installer
<!-- featureliftbench:behavior-clauses:end -->
