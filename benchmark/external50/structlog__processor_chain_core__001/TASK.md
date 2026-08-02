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

- `configure` callable must exist
- `get_logger` callable must exist
- `reset_defaults` callable must exist
- `processors.JSONRenderer` class must be importable
- `processors.KeyValueRenderer` class must be importable
- `processors.TimeStamper` class must be importable
- `processors.add_log_level` callable must exist

## Required Behavior

- The extracted feature must support this observable behavior: configure processor chain with JSONRenderer and bind context. Required observable cases include bind and json renderer; key value renderer.
- The extracted feature must support this observable behavior: TimeStamper/add_log_level and unbind/new context. Required observable cases include timestamp and unbind; new context.
- The extracted feature must support this observable behavior: processors run in configure order. Required observable cases include processor order.
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

- **B001** — The extracted feature must support this observable behavior: configure processor chain with JSONRenderer and bind context. Required observable cases include bind and json renderer; key value renderer.
- **B002** — The extracted feature must support this observable behavior: TimeStamper/add_log_level and unbind/new context. Required observable cases include timestamp and unbind; new context.
- **B003** — The extracted feature must support this observable behavior: processors run in configure order. Required observable cases include processor order.
- **B004** — reset_defaults clears global configuration between tests.
- **B005** — The package exposes the required task API paths `featurelifted.configure`, `featurelifted.get_logger`, `featurelifted.reset_defaults`, and the frozen processors with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: structlog.
<!-- featureliftbench:behavior-clauses:end -->
