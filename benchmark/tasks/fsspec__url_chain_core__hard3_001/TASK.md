# FeatureLift Task: url_to_fs

Extract fsspec URL chain resolution into `featurelifted`.

## Target API

```python
from featurelifted import ProtocolRegistry, url_to_fs, UnknownProtocolError
```

## Required Behavior

- `ProtocolRegistry` resolves protocol names and aliases.
- `url_to_fs` parses chained URLs and merges query/storage options.
- Unknown protocols raise `UnknownProtocolError`.

## Constraints

- Forbidden imports: `fsspec`.
- No remote filesystem operations.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — protocol registry
- **B002** — chained URL unwrapping
- **B003** — storage_options parsing
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: fsspec
<!-- featureliftbench:behavior-clauses:end -->
