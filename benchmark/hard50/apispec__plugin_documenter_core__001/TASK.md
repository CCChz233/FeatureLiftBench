# FeatureLift Task: OpenAPI plugin documenter

Build a standalone `featurelifted` package providing `APISpec` path and schema recording plus `BasePlugin` helpers.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    APISpec,
    BasePlugin,
)
```

## Required API Details

- `APISpec(title: str, version: str, openapi_version: str, plugins: Sequence[BasePlugin] = (), **options)` class constructor
  - `APISpec.__init__(self, title: str, version: str, openapi_version: str, plugins: Sequence[BasePlugin] = (), **options) -> None`
  - `APISpec.path(self, path: str | None = None, *, operations: dict | None = None, summary: str | None = None, description: str | None = None, parameters: list[dict] | None = None, **kwargs) -> APISpec`
  - `APISpec.to_dict(self) -> dict`
  - `APISpec.components` attribute must exist on instances
- `BasePlugin()` class constructor
  - `BasePlugin.init_spec(self, spec: APISpec) -> None`
  - `BasePlugin.path_helper(self, path: str | None = None, operations: dict | None = None, parameters: list[dict] | None = None, **kwargs) -> str | None`

## Required Behavior

- Calling `APISpec.path` with a path and operations records that path under `to_dict()['paths']`.
- Calling `spec.components.schema(name, schema)` records the named schema under `to_dict()['components']['schemas']`.
- When an `APISpec` is constructed with plugins, each plugin's `init_spec` runs during construction and receives that spec.
- A plugin `path_helper` may supply missing operations or rewrite the path string stored in the spec.
- The package exposes `APISpec` and `BasePlugin` with construction, `path`, `to_dict`, `init_spec`, and `path_helper` as listed in this contract.
- The submitted package source does not import the forbidden upstream package `apispec`.

## Constraints

- Forbidden imports: `apispec`.
- Do not implement Marshmallow plugin.
- Do not implement YAML dumping of remote URLs.
- Do not implement runtime import of apispec.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — Calling `APISpec.path` with a path and operations records that path under `to_dict()['paths']`.
- **B002** — Calling `spec.components.schema(name, schema)` records the named schema under `to_dict()['components']['schemas']`.
- **B003** — When an `APISpec` is constructed with plugins, each plugin's `init_spec` runs during construction and receives that spec.
- **B004** — A plugin `path_helper` may supply missing operations or rewrite the path string stored in the spec.
- **B005** — The package exposes `APISpec` and `BasePlugin` with construction, `path`, `to_dict`, `init_spec`, and `path_helper` as listed in this contract.
- **B006** — The submitted package source does not import the forbidden upstream package `apispec`.
<!-- featureliftbench:behavior-clauses:end -->
