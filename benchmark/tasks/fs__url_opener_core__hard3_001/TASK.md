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
