# FeatureLift Task: Retry decorator and context policy

Extract stamina retry and retry_context with deterministic zero-wait policy controls.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    Attempt,
    retry,
    retry_context,
    set_active,
    set_testing,
)
```

## Required API Details

- `retry(*, on, attempts=10, timeout=45.0, wait_initial=0.1, wait_max=5.0, wait_jitter=1.0, wait_exp_base=2)`
- `retry_context(on, attempts=10, timeout=45.0, wait_initial=0.1, wait_max=5.0, wait_jitter=1.0, wait_exp_base=2)`
- `Attempt` class must be importable
  - `Attempt.num` attribute must exist on instances
  - `Attempt.next_wait` attribute must exist on instances
- `set_active(active: bool) -> None`
- `set_testing(testing: bool) -> None`

## Required Behavior

- retry retries only configured exceptions and returns the first successful result.
- retry_context exposes one-based Attempt.num values and stops at the configured attempt limit.
- set_active and set_testing change retry execution policy without changing the wrapped callable API.
- The submitted package uses only the locked tenacity dependency and does not import stamina.

## Constraints

- Forbidden imports: `stamina`.
- Do not implement async and Trio integration.
- Do not implement logging instrumentation adapters.
- Do not implement non-zero sleeps in evaluator tests.
- Do not implement original stamina import at runtime.

## Public vs Hidden Tests

Public tests cover common use. Hidden tests cover documented edge, configuration, state, API-surface, and isolation behavior only.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — retry retries only configured exceptions and returns the first successful result.
- **B002** — retry_context exposes one-based Attempt.num values and stops at the configured attempt limit.
- **B003** — set_active and set_testing change retry execution policy without changing the wrapped callable API.
- **B004** — The submitted package uses only the locked tenacity dependency and does not import stamina.
<!-- featureliftbench:behavior-clauses:end -->
