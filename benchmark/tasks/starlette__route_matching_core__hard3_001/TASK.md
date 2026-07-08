# FeatureLift Task: Route matching and URL path convertor registry

Extract route matching subset into `featurelifted`.

## Target API

```python
from featurelifted import compile_path, Route, Mount, Router, Match
```

## Required Behavior

- `Route.matches` and `Router.match` resolve paths with typed convertors.
- `Mount` matches child routes under a path prefix.
- `Router.url_path_for(route_name, **path_params)` reverses URLs for named routes.

## Constraints

- Forbidden imports: `starlette`.
- No ASGI server or middleware.
