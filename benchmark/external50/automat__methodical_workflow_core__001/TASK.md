# FeatureLift Task: Methodical state-machine workflow

Extract MethodicalMachine declaration, transition dispatch, outputs, and state serialization.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    MethodicalMachine,
    NoTransition,
)
```

## Required API Details

- `MethodicalMachine` class must be importable
- `NoTransition` must be importable and raisable

## Required Behavior

- MethodicalMachine composes declared states and inputs into deterministic transitions on host instances.
- Transition outputs are collected and returned in declared order.
- Serializer and unserializer decorators round-trip the active state for a new instance.
- The submitted package does not import automat or use visualization dependencies.

## Constraints

- Forbidden imports: `automat`.
- Do not implement Graphviz rendering.
- Do not implement Twisted integration.
- Do not implement command-line visualization.
- Do not implement original automat import at runtime.

## Public vs Hidden Tests

Public tests cover common use. Hidden tests cover documented edge, configuration, state, API-surface, and isolation behavior only.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — MethodicalMachine composes declared states and inputs into deterministic transitions on host instances.
- **B002** — Transition outputs are collected and returned in declared order.
- **B003** — Serializer and unserializer decorators round-trip the active state for a new instance.
- **B004** — The submitted package does not import automat or use visualization dependencies.
<!-- featureliftbench:behavior-clauses:end -->
