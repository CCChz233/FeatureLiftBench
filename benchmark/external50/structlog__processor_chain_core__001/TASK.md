# FeatureLift Task: structlog processor chain

Extract a task-scoped subset of `structlog` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    configure,
    get_logger,
    processors,
    reset_defaults,
)
```

## Required API Details

- `configure(*, processors, logger_factory, cache_logger_on_first_use=False)`
- `get_logger(*args, **initial_values)`
- `reset_defaults() -> None`
- `processors.JSONRenderer` class must be importable
- `processors.KeyValueRenderer` class must be importable
- `processors.TimeStamper` class must be importable
- `processors.add_log_level(logger, method_name, event_dict)`

## Required Behavior

- configure installs a processor chain and logger factory; bound context and event fields reach JSONRenderer output, while TimeStamper(fmt='iso') and add_log_level add timestamp and level fields before rendering.
- KeyValueRenderer emits event fields as key-value text; bound loggers support unbind to remove keys and new to replace the prior context before emitting an event.
- Processors run exactly once in the order supplied to configure before the final rendered value is passed to the wrapped logger.
- reset_defaults clears global configuration between tests.
- The package exposes the required task API paths `featurelifted.configure`, `featurelifted.get_logger`, `featurelifted.reset_defaults`, and the frozen processors with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: structlog.

## Constraints

- Forbidden imports: `structlog`.
- Do not implement twisted/asyncio.
- Do not implement stdlib LoggerFactory integrations.
- Do not implement original structlog import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — configure installs a processor chain and logger factory; bound context and event fields reach JSONRenderer output, while TimeStamper(fmt='iso') and add_log_level add timestamp and level fields before rendering.
- **B002** — KeyValueRenderer emits event fields as key-value text; bound loggers support unbind to remove keys and new to replace the prior context before emitting an event.
- **B003** — Processors run exactly once in the order supplied to configure before the final rendered value is passed to the wrapped logger.
- **B004** — reset_defaults clears global configuration between tests.
- **B005** — The package exposes the required task API paths `featurelifted.configure`, `featurelifted.get_logger`, `featurelifted.reset_defaults`, and the frozen processors with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: structlog.
<!-- featureliftbench:behavior-clauses:end -->
