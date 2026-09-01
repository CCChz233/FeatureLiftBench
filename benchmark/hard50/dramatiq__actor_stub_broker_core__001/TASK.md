# FeatureLift Task: Actor send on StubBroker

Build a standalone `featurelifted` package providing Dramatiq-style actors that enqueue on an in-process `StubBroker` with middleware hooks.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    actor,
    get_broker,
    Middleware,
    set_broker,
    StubBroker,
)
```

## Required API Details

- `actor(fn=None, *, max_retries=None, **kwargs)`
- `StubBroker(middleware=None)` class constructor
  - `StubBroker.add_middleware(self, middleware) -> None`
- `Middleware()` class constructor
  - `Middleware.before_enqueue(self, broker, message, delay) -> None`
  - `Middleware.after_enqueue(self, broker, message, delay) -> None`
- `set_broker(broker) -> None`
- `get_broker() -> Broker`

## Required Behavior

- After `set_broker` with a `StubBroker`, an `@actor` function's `send` enqueues a message on that in-process broker without contacting RabbitMQ or Redis.
- Middleware registered with `StubBroker.add_middleware` runs `before_enqueue` then `after_enqueue` around `send`, receiving the actor name of the enqueued message.
- `get_broker()` returns the broker previously installed with `set_broker`. An actor declared with `max_retries=0` stores that option on the actor.
- The in-process stub path does not start a worker loop or open a network connection; enqueue is enough to observe send and middleware.
- The package exposes `actor`, `StubBroker`, `Middleware`, `set_broker`, and `get_broker` as listed in this contract.
- The submitted package source does not import the forbidden upstream package `dramatiq`.

## Constraints

- Forbidden imports: `dramatiq`.
- Do not implement RabbitMQ broker.
- Do not implement Redis broker.
- Do not implement worker process loops.
- Do not implement runtime import of dramatiq.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — After `set_broker` with a `StubBroker`, an `@actor` function's `send` enqueues a message on that in-process broker without contacting RabbitMQ or Redis.
- **B002** — Middleware registered with `StubBroker.add_middleware` runs `before_enqueue` then `after_enqueue` around `send`, receiving the actor name of the enqueued message.
- **B003** — `get_broker()` returns the broker previously installed with `set_broker`. An actor declared with `max_retries=0` stores that option on the actor.
- **B004** — The in-process stub path does not start a worker loop or open a network connection; enqueue is enough to observe send and middleware.
- **B005** — The package exposes `actor`, `StubBroker`, `Middleware`, `set_broker`, and `get_broker` as listed in this contract.
- **B006** — The submitted package source does not import the forbidden upstream package `dramatiq`.
<!-- featureliftbench:behavior-clauses:end -->
