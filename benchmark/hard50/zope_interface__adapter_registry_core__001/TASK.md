# FeatureLift Task: Interface declarations and adapter registry lookup

Extract the pure-Python interface declaration and adapter lookup core into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    AdapterRegistry,
    implementer,
    Interface,
    providedBy,
)
```

## Required API Details

- `Interface()` class constructor
- `implementer(*interfaces: Interface) -> Callable[[type], type]`
- `providedBy(obj: object) -> InterfaceSpecification`
- `AdapterRegistry(bases: tuple[AdapterRegistry, ...] = ())` class constructor
  - `AdapterRegistry.register(self, required, provided, name: str, value) -> None`
  - `AdapterRegistry.registered(self, required, provided, name: str = '')`
  - `AdapterRegistry.unregister(self, required, provided, name: str, value=None) -> bool`
  - `AdapterRegistry.lookup(self, required, provided, name: str = '', default=None)`
  - `AdapterRegistry.lookupAll(self, required, provided) -> tuple[tuple[str, object], ...]`
  - `AdapterRegistry.queryAdapter(self, obj, provided, name: str = '', default=None)`
  - `AdapterRegistry.queryMultiAdapter(self, objects, provided, name: str = '', default=None)`

## Required Behavior

- When a class is decorated with `implementer(IFoo)`, `providedBy(instance)` contains `IFoo`, and `IFoo.providedBy(instance)` is true for that instance and its subclasses.
- After a one-object adapter factory is registered for a required interface and provided interface, `queryAdapter` calls the factory with the object and returns its result; a missing registration or a factory result of `None` yields the supplied default.
- Registrations are separated by text name: named and unnamed adapters can coexist, `registered` reports only an exact registration, and `unregister` removes only the matching registration and value.
- For a multi-adapter registration, `queryMultiAdapter` selects against every object's provided interfaces, calls the factory with the objects in order, and returns the supplied default when no match exists.
- Adapter lookup honors interface inheritance in both directions relevant to dispatch: an object providing a derived required interface matches a base-required registration, and an adapter registered as providing a derived interface can satisfy a base-interface lookup.
- `lookupAll` returns one effective `(name, value)` pair per matching name, with registrations in the current registry taking precedence over registrations inherited from base registries.

## Constraints

- Forbidden imports: `zope.interface`.
- Do not implement C acceleration modules.
- Do not implement global component site managers and utility registration.
- Do not implement subscription adapters, handlers, persistence, and ZODB integration.
- Do not implement runtime import of `zope.interface`.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — When a class is decorated with `implementer(IFoo)`, `providedBy(instance)` contains `IFoo`, and `IFoo.providedBy(instance)` is true for that instance and its subclasses.
- **B002** — After a one-object adapter factory is registered for a required interface and provided interface, `queryAdapter` calls the factory with the object and returns its result; a missing registration or a factory result of `None` yields the supplied default.
- **B003** — Registrations are separated by text name: named and unnamed adapters can coexist, `registered` reports only an exact registration, and `unregister` removes only the matching registration and value.
- **B004** — For a multi-adapter registration, `queryMultiAdapter` selects against every object's provided interfaces, calls the factory with the objects in order, and returns the supplied default when no match exists.
- **B005** — Adapter lookup honors interface inheritance in both directions relevant to dispatch: an object providing a derived required interface matches a base-required registration, and an adapter registered as providing a derived interface can satisfy a base-interface lookup.
- **B006** — `lookupAll` returns one effective `(name, value)` pair per matching name, with registrations in the current registry taking precedence over registrations inherited from base registries.
<!-- featureliftbench:behavior-clauses:end -->
