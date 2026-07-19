# FeatureLift Task: HookCaller historic wrapper ordering

Extract pluggy hook caller historic/wrapper behavior into `featurelifted`.

## Target API

```python
from featurelifted import HookCaller
```

## Required Behavior

- `HookCaller` supports historic hooks via `call_historic()` and replays history for late registrations.
- Hook wrappers run teardown in reverse registration order after inner implementations.
- `tryfirst`/`trylast` options control hookimpl ordering.
- `call_extra()` temporarily adds hook implementations without mutating permanent state.

## Constraints

- Forbidden imports: `pluggy`.
- No plugin manager or entry point discovery.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — historic hook replay
- **B002** — hookwrapper ordering
- **B003** — multicall result aggregation
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: pluggy
<!-- featureliftbench:behavior-clauses:end -->
