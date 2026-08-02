# FeatureLift Task: invoke collection context

Extract a task-scoped subset of `invoke` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    Collection,
    Context,
    MockContext,
    task,
    UnexpectedExit,
)
```

## Required API Details

- `task` callable must exist
- `Collection` class must be importable
  - `Collection.add_task` callable must exist
  - `Collection.add_collection` callable must exist
- `Context` class must be importable
- `MockContext` class must be importable
  - `MockContext.run` callable must exist
- `UnexpectedExit` class must be importable

## Required Behavior

- The extracted feature must support this observable behavior: Collection task invocation with Context. Required observable cases include collection task call.
- The extracted feature must support this observable behavior: MockContext stubs run without shell. Required observable cases include mock context run.
- The extracted feature must support this observable behavior: nested collections and UnexpectedExit. Required observable cases include nested collection; task exception type.
- Tasks are accessed via Collection.__getitem__ by name.
- The package exposes task/Collection/Context/MockContext/UnexpectedExit with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: invoke.

## Constraints

- Forbidden imports: `invoke`.
- Do not implement real SSH fabric.
- Do not implement original invoke import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: Collection task invocation with Context. Required observable cases include collection task call.
- **B002** — The extracted feature must support this observable behavior: MockContext stubs run without shell. Required observable cases include mock context run.
- **B003** — The extracted feature must support this observable behavior: nested collections and UnexpectedExit. Required observable cases include nested collection; task exception type.
- **B004** — Tasks are accessed via Collection.__getitem__ by name.
- **B005** — The package exposes task/Collection/Context/MockContext/UnexpectedExit with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: invoke.
<!-- featureliftbench:behavior-clauses:end -->
