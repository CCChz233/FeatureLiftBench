# FeatureLift Task: Hierarchical state machine transition core

Extract a synchronous subset of pytransitions into `featurelifted`.

## Target API

```python
from featurelifted import Machine, MachineError, EventData
```

## Required Behavior

- Register states and transitions; bind trigger methods on the model.
- Execute `before`/`after` callbacks and machine-level before/after state change callbacks.
- Support transition `conditions` that can veto a transition.
- Support dotted nested state names such as `parent.child`.
- Raise `MachineError` for invalid triggers unless `ignore_invalid_triggers=True`.

## Constraints

- Forbidden imports: `transitions`.
- No async, graph, or extension modules.
