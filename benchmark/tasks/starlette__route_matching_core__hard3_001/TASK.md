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

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — path compile/match
- **B002** — convertor registry
- **B003** — mount prefix matching
- **B004** — url reversing
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: starlette
<!-- featureliftbench:behavior-clauses:end -->
