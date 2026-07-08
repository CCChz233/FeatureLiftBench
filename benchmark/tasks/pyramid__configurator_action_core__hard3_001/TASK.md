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
