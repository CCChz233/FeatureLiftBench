# FeatureLift Task: build_url normalize_headers

Extract aiohttp URL/header helpers into `featurelifted`.

## Target API

```python
from featurelifted import build_url, normalize_headers, CIMultiDict, InvalidHeaderName
```

## Required Behavior

- `build_url` merges query parameters into a base URL.
- `normalize_headers` returns a case-insensitive `CIMultiDict`.
- Invalid header names raise `InvalidHeaderName`.

## Constraints

- Forbidden imports: `aiohttp`.
- No client/server or async runtime.
