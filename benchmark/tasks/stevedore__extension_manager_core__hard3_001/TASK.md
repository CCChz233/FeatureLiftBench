# FeatureLift Task: ExtensionManager entry point discovery and loading

Extract a task-scoped subset of Stevedore's extension manager into a standalone `featurelifted` package.

The implementation must not import `stevedore`, must not read from `repo/`, must not use the network, and must not depend on external services. Use only the standard library.

## Target API

```python
from featurelifted import (
    EntryPointSpec,
    Extension,
    ExtensionManager,
    MultipleMatches,
    NamedExtensionManager,
    NoMatches,
    error_on_conflict,
    ignore_conflicts,
)
```

Required manager behavior:

- `ExtensionManager(namespace, entry_points=None, invoke_on_load=False, invoke_args=None, invoke_kwds=None, propagate_map_exceptions=False, on_load_failure_callback=None, conflict_resolver=ignore_conflicts)`
- `NamedExtensionManager(namespace, names, entry_points=None, ..., name_order=False, on_missing_entrypoints_callback=None)`
- `EntryPointSpec(name, value, group, loader=None)` for deterministic tests.

## Required Behavior

- Filter entry points by namespace before loading.
- Load plugins through `entry_point.load()`.
- If `invoke_on_load=True`, instantiate/call the loaded plugin with `invoke_args` and `invoke_kwds` and store the object on `Extension.obj`.
- On plugin load failure, invoke `on_load_failure_callback(manager, entry_point, exception)` and skip the failed extension.
- Provide `names()`, `entry_points_names()`, iteration, containment, `__getitem__`, `items()`, `map()`, and `map_method()`.
- `map()` raises `NoMatches` when no extensions are loaded.
- `map()` ignores callback exceptions unless `propagate_map_exceptions=True`.
- Duplicate names resolve to the last extension by default through `ignore_conflicts`.
- `error_on_conflict` raises `MultipleMatches` when duplicate names are looked up.
- `NamedExtensionManager` filters by requested names, reports missing names, and can preserve requested order.

## Constraints

- Forbidden imports: `stevedore`.
- Forbidden path access: `repo/`, `stevedore/`.
- Do not implement driver, dispatch, hook, Sphinx, or example modules.
- Do not depend on installed third-party entry points in tests; use injected `entry_points`.

## Public vs Hidden Tests

Public tests cover namespace filtering, plugin loading, invoke-on-load, `map_method`, and empty-manager errors.
Hidden tests cover load failure callbacks, duplicate-name conflict semantics, map exception propagation, and named manager filtering/order/missing behavior.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — EntryPointSpec test entry points
- **B002** — Extension bookkeeping
- **B003** — ExtensionManager namespace filtering and loading
- **B004** — invoke_on_load and invoke_args/invoke_kwds
- **B005** — on_load_failure_callback
- **B006** — names, items, iteration, containment, getitem
- **B007** — map and map_method
- **B008** — duplicate-name conflict resolvers
- **B009** — NamedExtensionManager filtering, missing callback, and requested order
- **B010** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B011** — the submitted package does not import forbidden upstream packages: stevedore
<!-- featureliftbench:behavior-clauses:end -->
