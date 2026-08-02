# FeatureLift Task: JSON-defined statechart workflow

Extract safe inline JSON statechart loading and synchronous event execution.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    InvalidDefinition,
    load,
    StateChart,
)
```

## Required API Details

- `load(source: str | Path, *, format=None, trusted=False, validate=False, name=None) -> type[StateChart]`
- `StateChart` class must be importable
  - `StateChart.send(event, *args, **kwargs)`
  - `StateChart.configuration` attribute must exist on instances
- `InvalidDefinition` must be importable and raisable

## Required Behavior

- load parses an inline JSON statechart definition and returns an instantiable StateChart subclass.
- The instantiated chart starts in the configured initial state and routes declared events to target states.
- The default trusted=False mode rejects unsupported executable expressions at load time.
- The submitted package does not import statemachine and performs no file or network lookup for inline JSON.

## Constraints

- Forbidden imports: `statemachine`.
- Do not implement YAML and SCXML.
- Do not implement schema validation.
- Do not implement trusted eval.
- Do not implement Django integration.
- Do not implement original statemachine import at runtime.

## Public vs Hidden Tests

Public tests cover common use. Hidden tests cover documented edge, configuration, state, API-surface, and isolation behavior only.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — load parses an inline JSON statechart definition and returns an instantiable StateChart subclass.
- **B002** — The instantiated chart starts in the configured initial state and routes declared events to target states.
- **B003** — The default trusted=False mode rejects unsupported executable expressions at load time.
- **B004** — The submitted package does not import statemachine and performs no file or network lookup for inline JSON.
<!-- featureliftbench:behavior-clauses:end -->
