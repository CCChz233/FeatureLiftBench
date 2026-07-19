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

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — state machine trigger execution
- **B002** — conditional transitions
- **B003** — before/after callbacks
- **B004** — nested dotted states
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: transitions
<!-- featureliftbench:behavior-clauses:end -->
