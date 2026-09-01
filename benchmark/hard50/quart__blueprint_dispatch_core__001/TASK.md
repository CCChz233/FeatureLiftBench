# FeatureLift Task: Blueprint routing

Build a standalone `featurelifted` package providing Quart-style app and blueprint HTTP routing through an in-process test client, without binding sockets.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    Blueprint,
    Quart,
)
```

## Required API Details

- `Quart(import_name: str, static_url_path: str | None = None, static_folder: str | None = 'static', static_host: str | None = None, host_matching: bool = False, subdomain_matching: bool = False, template_folder: str | os.PathLike[str] | None = 'templates', instance_path: str | None = None, instance_relative_config: bool = False, root_path: str | None = None)` class constructor
  - `Quart.__init__(self, import_name: str, static_url_path: str | None = None, static_folder: str | None = 'static', static_host: str | None = None, host_matching: bool = False, subdomain_matching: bool = False, template_folder: str | os.PathLike[str] | None = 'templates', instance_path: str | None = None, instance_relative_config: bool = False, root_path: str | None = None) -> None`
  - `Quart.route(self, rule: str, **options: Any)`
  - `Quart.register_blueprint(self, blueprint: Blueprint, **options: Any) -> None`
  - `Quart.test_client(self, use_cookies: bool = True, **kwargs: Any)`
- `Blueprint(name: str, import_name: str, *args, **kwargs)` class constructor
  - `Blueprint.__init__(self, *args: Any, **kwargs: Any) -> None`
  - `Blueprint.route(self, rule: str, **options: Any)`

## Required Behavior

- After `@app.route(path)` registers an async view, `app.test_client().get(path)` returns status 200 and the view body.
- After a `Blueprint` is registered with `url_prefix`, a GET to `{url_prefix}{rule}` returns status 200 and the blueprint view body.
- A GET to a path that matches no registered rule returns status 404.
- Two blueprints registered with different prefixes dispatch independently: each prefix serves its own rule, and a rule from one blueprint is not found under the other prefix.
- The package exposes `Quart` and `Blueprint` with construction, `route`, `register_blueprint`, and `test_client` as listed in this contract.
- The submitted package source does not import the forbidden upstream package `quart`.

## Constraints

- Forbidden imports: `quart`.
- Do not implement hypercorn.serve / bind sockets.
- Do not implement production ASGI server.
- Do not implement websocket serving.
- Do not implement runtime import of quart.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — After `@app.route(path)` registers an async view, `app.test_client().get(path)` returns status 200 and the view body.
- **B002** — After a `Blueprint` is registered with `url_prefix`, a GET to `{url_prefix}{rule}` returns status 200 and the blueprint view body.
- **B003** — A GET to a path that matches no registered rule returns status 404.
- **B004** — Two blueprints registered with different prefixes dispatch independently: each prefix serves its own rule, and a rule from one blueprint is not found under the other prefix.
- **B005** — The package exposes `Quart` and `Blueprint` with construction, `route`, `register_blueprint`, and `test_client` as listed in this contract.
- **B006** — The submitted package source does not import the forbidden upstream package `quart`.
<!-- featureliftbench:behavior-clauses:end -->
