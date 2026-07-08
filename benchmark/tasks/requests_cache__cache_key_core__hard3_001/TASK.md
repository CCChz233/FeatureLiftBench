# FeatureLift Task: HTTP request cache key and expiration policy

Extract a task-scoped subset of `requests-cache` cache key generation and expiration policy into a standalone `featurelifted` package.

The implementation must not import `requests_cache`, `requests`, or `url_normalize`, must not read from `repo/`, must not use the network, and must not depend on external services. Use only the standard library.

## Target API

```python
from featurelifted import CachePolicy, create_cache_key, create_key, get_expiration

create_key(method, url, params=None, headers=None, body=None, ignored_parameters=None, match_headers=False, verify=True, serializer=None, content_root_key=None) -> str
create_cache_key(request, **kwargs) -> str
get_expiration(headers, default=None, now=None) -> int | None
CachePolicy.from_headers(headers, default=None, now=None)
```

Also expose `normalize_url`, `normalize_params`, `normalize_headers`, `normalize_body`, and `get_matched_headers`.

## Required Behavior

- Normalize method to uppercase.
- Normalize URL scheme/host case and query parameter ordering.
- Merge explicit `params` with query parameters already present in the URL.
- Redact ignored parameter values in URL/query, headers, form body, and JSON body.
- Normalize JSON request bodies by sorting keys.
- Normalize form-encoded bodies like query parameters.
- Headers affect cache keys only when `match_headers` is truthy.
- Multi-value header values are lowercased, trimmed, sorted, and rejoined.
- `Cache-Control: no-store` disables storage.
- `Cache-Control: max-age=N` sets expiration to `N` seconds.
- `Expires` is converted to seconds relative to an explicit `now`.
- Use `default` expiration when no cache header applies.

## Constraints

- Forbidden imports: `requests_cache`, `requests`, `url_normalize`.
- Forbidden path access: `repo/`, `requests_cache/`.
- Do not implement sessions, adapters, serializers, or cache backends.
- Do not use network, Redis, MongoDB, SQLite, browser, or external APIs.

## Public vs Hidden Tests

Public tests cover query ordering, ignored query parameters, request compatibility helper behavior, and Cache-Control `max-age` / `no-store`.
Hidden tests cover JSON body normalization, form body normalization, key-only query params, selected-header matching, multi-value header normalization, redaction, Expires, and default expiration.
