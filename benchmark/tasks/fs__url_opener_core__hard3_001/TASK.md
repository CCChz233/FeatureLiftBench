# FeatureLift Task: parse_fs_url FSOpenerRegistry

Extract pyfilesystem2 URL opener parsing into `featurelifted`.

## Target API

```python
from featurelifted import parse_fs_url, FSOpenerRegistry, ParseError, UnsupportedProtocolError
```

## Required Behavior

- `parse_fs_url` parses `scheme://resource!path` URLs and query parameters.
- `FSOpenerRegistry` registers opener factories and opens URLs.
- Invalid URLs raise `ParseError`; unknown schemes raise `UnsupportedProtocolError`.

## Constraints

- Forbidden imports: `fs`.
- No real filesystem backends beyond in-memory fakes.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — FS URL parsing
- **B002** — opener registry
- **B003** — path normalization
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: fs
<!-- featureliftbench:behavior-clauses:end -->
