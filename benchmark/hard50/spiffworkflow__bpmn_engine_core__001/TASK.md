# FeatureLift Task: In-memory BPMN engine

Build a standalone `featurelifted` package that parses a tiny in-memory BPMN document and runs start, script, and user-task processes to a completed or waiting state.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    BpmnParser,
    BpmnWorkflow,
)
```

## Required API Details

- `BpmnParser()` class constructor
  - `BpmnParser.add_bpmn_str(self, bpmn_str, filename=None)`
  - `BpmnParser.get_spec(self, process_id, required=True)`
- `BpmnWorkflow(spec)` class constructor
  - `BpmnWorkflow.do_engine_steps(self, will_complete_task=None, did_complete_task=None)`
  - `BpmnWorkflow.is_completed(self) -> bool`
  - `BpmnWorkflow.data` attribute must exist on instances

## Required Behavior

- `BpmnParser.add_bpmn_str` accepts an in-memory BPMN document and `get_spec(process_id)` returns the process with that id so it can be wrapped in `BpmnWorkflow`.
- A process that is only a start event, a script task assigning `result = 1 + 2`, and an end event reaches a completed state after `do_engine_steps()`, and the workflow data contains `result` equal to 3.
- A process whose next work is a user task is not completed after `do_engine_steps()` because that waiting task is not an automatic engine step.
- The engine runs entirely in memory from the XML string; tests do not read `repo/` or contact a network service.
- The package exposes `BpmnParser` and `BpmnWorkflow` with `add_bpmn_str`, `get_spec`, `do_engine_steps`, and `is_completed`.
- The submitted package source does not import the forbidden upstream package `SpiffWorkflow`.

## Constraints

- Forbidden imports: `SpiffWorkflow`.
- Do not implement BPMN editor UI.
- Do not implement full DMN decision tables.
- Do not implement runtime import of SpiffWorkflow.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — `BpmnParser.add_bpmn_str` accepts an in-memory BPMN document and `get_spec(process_id)` returns the process with that id so it can be wrapped in `BpmnWorkflow`.
- **B002** — A process that is only a start event, a script task assigning `result = 1 + 2`, and an end event reaches a completed state after `do_engine_steps()`, and the workflow data contains `result` equal to 3.
- **B003** — A process whose next work is a user task is not completed after `do_engine_steps()` because that waiting task is not an automatic engine step.
- **B004** — The engine runs entirely in memory from the XML string; tests do not read `repo/` or contact a network service.
- **B005** — The package exposes `BpmnParser` and `BpmnWorkflow` with `add_bpmn_str`, `get_spec`, `do_engine_steps`, and `is_completed`.
- **B006** — The submitted package source does not import the forbidden upstream package `SpiffWorkflow`.
<!-- featureliftbench:behavior-clauses:end -->
