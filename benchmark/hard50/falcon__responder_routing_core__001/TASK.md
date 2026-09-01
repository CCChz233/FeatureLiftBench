# FeatureLift Task: WSGI responder routing

Build a standalone `featurelifted` package providing Falcon-style `App.add_route` dispatch for WSGI environ dicts without binding a socket.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    App,
)
```

## Required API Details

- `App(media_type='application/json', request_type=None, response_type=None, middleware=None, router=None, independent_middleware=True, cors_enable=False, sink_before_static_route=True)` class constructor
  - `App.__init__(self, media_type='application/json', request_type=None, response_type=None, middleware=None, router=None, independent_middleware=True, cors_enable=False, sink_before_static_route=True) -> None`
  - `App.add_route(self, uri_template: str, resource: object, **kwargs) -> None`
  - `App.__call__(self, env, start_response)`

## Required Behavior

- After `add_route` registers a resource with `on_get`, a WSGI GET to that path returns HTTP 200 and the responder body.
- A template such as `/items/{item_id}` captures the path segment and passes it to the responder.
- A request whose path matches no registered route is answered with HTTP 404.
- A request whose path matches a route that has no responder for that HTTP method is answered with HTTP 405.
- The package exposes `App` with construction, `add_route`, and WSGI `__call__` as listed in this contract.
- The submitted package source does not import the forbidden upstream package `falcon`.

## Constraints

- Forbidden imports: `falcon`.
- Do not implement ASGI lifespan servers.
- Do not implement WebSocket.
- Do not implement real listen/bind.
- Do not implement runtime import of falcon.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — After `add_route` registers a resource with `on_get`, a WSGI GET to that path returns HTTP 200 and the responder body.
- **B002** — A template such as `/items/{item_id}` captures the path segment and passes it to the responder.
- **B003** — A request whose path matches no registered route is answered with HTTP 404.
- **B004** — A request whose path matches a route that has no responder for that HTTP method is answered with HTTP 405.
- **B005** — The package exposes `App` with construction, `add_route`, and WSGI `__call__` as listed in this contract.
- **B006** — The submitted package source does not import the forbidden upstream package `falcon`.
<!-- featureliftbench:behavior-clauses:end -->
