# FeatureLift Task: Dispatch table and Tools

Build a standalone `featurelifted` package providing CherryPy-style object-tree URL dispatch and Tool decorator configuration without binding sockets.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    Application,
    Dispatcher,
    expose,
    Tool,
)
```

## Required API Details

- `Application(root, script_name='', config=None)` class constructor
  - `Application.__init__(self, root, script_name='', config=None)`
  - `Application.__call__(self, environ, start_response)`
- `Dispatcher(dispatch_method_name=None, translate=punctuation_to_underscores)` class constructor
  - `Dispatcher.__init__(self, dispatch_method_name=None, translate=punctuation_to_underscores)`
  - `Dispatcher.find_handler(self, path)`
- `expose(func=None, alias=None)`
- `Tool(point, callable, name=None, priority=50)` class constructor
  - `Tool.__init__(self, point, callable, name=None, priority=50)`
  - `Tool.__call__(self, *args, **kwargs)`

## Required Behavior

- After page handlers are marked with `@expose`, calling a WSGI `Application` rooted at that object with a matching `PATH_INFO` and `HTTP_HOST` returns HTTP 200 and the handler body.
- A request whose `PATH_INFO` matches no exposed handler is answered with an HTTP 404 status.
- Decorating a function with `Tool('before_handler', hook, name='flag')()` sets `function._cp_config['tools.flag.on']` to True.
- An exposed nested object attribute is dispatched when `PATH_INFO` names that nested path, returning the nested handler body with HTTP 200.
- The package exposes `Application`, `Dispatcher`, `expose`, and `Tool` with the callable signatures listed in this contract.
- The submitted package source does not import the forbidden upstream package `cherrypy`.

## Constraints

- Forbidden imports: `cherrypy`.
- Do not implement engine.listen / bind sockets.
- Do not implement quickstart server loop.
- Do not implement production WSGI server.
- Do not implement runtime import of cherrypy.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — After page handlers are marked with `@expose`, calling a WSGI `Application` rooted at that object with a matching `PATH_INFO` and `HTTP_HOST` returns HTTP 200 and the handler body.
- **B002** — A request whose `PATH_INFO` matches no exposed handler is answered with an HTTP 404 status.
- **B003** — Decorating a function with `Tool('before_handler', hook, name='flag')()` sets `function._cp_config['tools.flag.on']` to True.
- **B004** — An exposed nested object attribute is dispatched when `PATH_INFO` names that nested path, returning the nested handler body with HTTP 200.
- **B005** — The package exposes `Application`, `Dispatcher`, `expose`, and `Tool` with the callable signatures listed in this contract.
- **B006** — The submitted package source does not import the forbidden upstream package `cherrypy`.
<!-- featureliftbench:behavior-clauses:end -->
