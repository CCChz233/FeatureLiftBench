# FeatureLift Task: Site manager utility lookup

Build a standalone `featurelifted` package providing site-manager utility registration and lookup by interface and optional name.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    ComponentLookupError,
    getGlobalSiteManager,
    getUtility,
    implementer,
    Interface,
    provideUtility,
    queryUtility,
)
```

## Required API Details

- `getUtility(interface, name='', context=None)`
- `queryUtility(interface, name='', default=None, context=None)`
- `provideUtility(component, provides=None, name='')`
- `getGlobalSiteManager()`
- `implementer(*interfaces)`
- `InterfaceInterface` class constructor
- `ComponentLookupError` must be importable and raisable

## Required Behavior

- After `provideUtility` registers an object for an interface, `getUtility` for that interface returns the same object.
- When no utility is registered for an interface, `queryUtility` returns the supplied default, or `None` when no default is given.
- When no utility is registered for an interface, `getUtility` raises `ComponentLookupError`.
- Utilities registered under different names for the same interface are returned independently by `getUtility(..., name=...)`.
- The package exposes `getUtility`, `queryUtility`, `provideUtility`, `getGlobalSiteManager`, `implementer`, `Interface`, and `ComponentLookupError` with the signatures listed in this contract.
- The submitted package source does not import the forbidden upstream package `zope.component`.

## Constraints

- Forbidden imports: `zope.component`.
- Do not implement persistent local sites.
- Do not implement ZODB.
- Do not implement runtime import of zope.component.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — After `provideUtility` registers an object for an interface, `getUtility` for that interface returns the same object.
- **B002** — When no utility is registered for an interface, `queryUtility` returns the supplied default, or `None` when no default is given.
- **B003** — When no utility is registered for an interface, `getUtility` raises `ComponentLookupError`.
- **B004** — Utilities registered under different names for the same interface are returned independently by `getUtility(..., name=...)`.
- **B005** — The package exposes `getUtility`, `queryUtility`, `provideUtility`, `getGlobalSiteManager`, `implementer`, `Interface`, and `ComponentLookupError` with the signatures listed in this contract.
- **B006** — The submitted package source does not import the forbidden upstream package `zope.component`.
<!-- featureliftbench:behavior-clauses:end -->
