# FeatureLift Task: Configurator action conflict resolver

Extract a Pyramid action registry subset into `featurelifted`.

## Target API

```python
from featurelifted import ActionRegistry, ConfigurationConflictError
```

## Required Behavior

- `register` queues actions with discriminators and order values.
- `commit` executes actions in order; duplicate discriminators raise `ConfigurationConflictError`.
- `None` discriminators never conflict.
- `introspect(category=...)` filters committed actions.

## Constraints

- Forbidden imports: `pyramid`.
- No WSGI/server.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — action registration
- **B002** — conflict detection
- **B003** — ordered commit
- **B004** — introspection
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: pyramid
<!-- featureliftbench:behavior-clauses:end -->
