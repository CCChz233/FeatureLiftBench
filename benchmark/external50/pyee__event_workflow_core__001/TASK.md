# FeatureLift Task: Event-emitter workflow orchestration

Extract synchronous EventEmitter registration, ordered dispatch, once semantics, and error routing.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    EventEmitter,
    PyeeError,
)
```

## Required API Details

- `EventEmitter` class must be importable
  - `EventEmitter.on(event: str, f=None)`
  - `EventEmitter.once(event: str, f=None)`
  - `EventEmitter.emit(event: str, *args, **kwargs) -> bool`
  - `EventEmitter.remove_listener(event: str, f) -> None`
  - `EventEmitter.remove_all_listeners(event=None) -> None`
  - `EventEmitter.listeners(event: str) -> list`
- `PyeeError` must be importable and raisable

## Required Behavior

- EventEmitter dispatches listeners synchronously in registration order and forwards arguments.
- once listeners remove themselves before invocation and listener removal updates subsequent dispatch.
- An unhandled error event raises its Exception or PyeeError for a non-exception payload.
- The submitted package uses only typing-extensions and does not import pyee.

## Constraints

- Forbidden imports: `pyee`.
- Do not implement asyncio, Trio, Twisted, and executor emitters.
- Do not implement thread scheduling.
- Do not implement network integration.
- Do not implement original pyee import at runtime.

## Public vs Hidden Tests

Public tests cover common use. Hidden tests cover documented edge, configuration, state, API-surface, and isolation behavior only.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — EventEmitter dispatches listeners synchronously in registration order and forwards arguments.
- **B002** — once listeners remove themselves before invocation and listener removal updates subsequent dispatch.
- **B003** — An unhandled error event raises its Exception or PyeeError for a non-exception payload.
- **B004** — The submitted package uses only typing-extensions and does not import pyee.
<!-- featureliftbench:behavior-clauses:end -->
