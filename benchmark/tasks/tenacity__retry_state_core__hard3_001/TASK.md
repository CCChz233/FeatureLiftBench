# FeatureLift Task: Retry state machine with stop/wait/retry predicates

Extract a synchronous subset of Tenacity's retry runtime into a standalone `featurelifted` package.

The implementation must not import `tenacity`, must not read from `repo/`, must not use the network, and must not depend on external services. Use only the standard library.

## Target API

```python
from featurelifted import (
    Retrying,
    RetryCallState,
    RetryError,
    retry_if_exception_type,
    retry_if_result,
    stop_after_attempt,
    stop_after_delay,
    stop_before_delay,
    wait_chain,
    wait_combine,
    wait_exponential,
    wait_fixed,
    wait_none,
)
```

Required call shape:

```python
Retrying(
    stop=None,
    wait=None,
    retry=None,
    sleep=None,
    before_sleep=None,
    reraise=False,
    retry_error_callback=None,
).__call__(fn, *args, **kwargs)
```

## Required Behavior

- Execute `fn` until the retry predicate returns false or the stop predicate triggers.
- Track a `RetryCallState` with `attempt_number`, `outcome`, `idle_for`, `upcoming_sleep`, and `seconds_since_start`.
- Support retry predicates:
  - `retry_if_exception_type`
  - `retry_if_result`
  - `|` and `&` composition through `retry_any` and `retry_all`
- Support stop policies:
  - `stop_after_attempt`
  - `stop_after_delay`
  - `stop_before_delay`
- Support wait policies:
  - `wait_fixed`
  - `wait_none`
  - `wait_chain`
  - `wait_combine`
  - `wait_exponential`
- `wait_chain()` with no strategies must raise `ValueError`.
- `before_sleep` must receive the state after `upcoming_sleep` is computed and before `idle_for` is incremented.
- When retries are exhausted:
  - use `retry_error_callback` when provided;
  - raise the last exception directly when `reraise=True` and the last outcome failed;
  - otherwise raise `RetryError`.

## Constraints

- Forbidden imports: `tenacity`.
- Forbidden path access: `repo/`, `tenacity/`.
- Do not implement async, Tornado, decorator overloads, or logging helper APIs.
- Do not actually sleep in tests unless the caller provides a sleep function that does so.

## Public vs Hidden Tests

Public tests cover exception retries, result retries, fixed waits, and exhausted retry errors.
Hidden tests cover wait-chain validation and exhaustion, callback state timing, `reraise`, retry predicate composition, and exponential wait behavior.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — Retrying callable execution loop
- **B002** — RetryCallState with attempt number, outcome, idle_for, and upcoming_sleep
- **B003** — RetryError and reraise behavior
- **B004** — retry_if_exception_type and retry_if_result
- **B005** — retry_any/retry_all composition via | and &
- **B006** — stop_after_attempt, stop_after_delay, stop_before_delay
- **B007** — wait_fixed, wait_none, wait_chain, wait_combine, wait_exponential
- **B008** — before_sleep and retry_error_callback
- **B009** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B010** — the submitted package does not import forbidden upstream packages: tenacity
<!-- featureliftbench:behavior-clauses:end -->
