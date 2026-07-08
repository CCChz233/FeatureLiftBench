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
