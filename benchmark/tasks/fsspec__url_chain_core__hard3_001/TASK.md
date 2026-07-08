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
