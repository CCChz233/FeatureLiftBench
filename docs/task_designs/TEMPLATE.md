# Task Design: `<task_id>`

> Machine-readable task spec: [TASK_FORMAT.md](../TASK_FORMAT.md). This file is the human design note.

Status: draft | oracle-verified | agent-calibrated

## Why This Task

Explain why this task belongs in FeatureLiftBench and what discrimination it provides (functional vs decoupling).

## Source

| Field | Value |
| --- | --- |
| Source repo | `<url>` |
| Commit | `<hash>` |
| License | `<SPDX>` |
| Language | Python |
| Difficulty | hard |
| Tags | multi-task-repo, `<discriminator-tag>` |

## Entanglement

```json
{
  "level": "high",
  "types": ["..."],
  "description": "...",
  "signals": ["..."]
}
```

## Target Feature

### Source entrypoints

- `...`

### Output API

```python
from featurelifted import ...
```

Primary callable:

```python
featurelifted.<callable>(...)
```

## Included Behaviors

- ...

## Excluded Behaviors

- CLI, original tests, docs, CI, packaging metadata
- Original package import at runtime
- Network / DB / GPU dependencies

## Environment

```json
{
  "python": "3.11",
  "network": false,
  "timeout_seconds": 60,
  "dependency_lock": "requirements.lock",
  "allowed_dependencies": [],
  "forbidden_dependencies": ["<original-package>"],
  "forbidden_imports": ["<original-package>"]
}
```

## Public Tests

Describe main-path behaviors visible to the agent. Do not expose combinator hidden edges.

- ...

## Hidden Tests

Force real decoupling. Include migrated edge cases and combinator scenarios.

- ...

## Module Probes

Each probe must be verified by removing the module from the oracle closure and confirming hidden failure.

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Probe-1 | `...` | `test_...` |
| Probe-2 | `...` | `test_...` |
| Probe-3 | `...` | `test_...` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | |
| Hidden tests | pass | |
| Forbidden import check | pass | |
| Oracle LOC | | |
| Source repo Python LOC | | |
| ExtractionRatio | 0.25–0.55 | |
| Copy-All functional gate | 1.0 | |
| Copy-All ExtractionRatio | ≥ 0.95 | |
| Module probes | all verified | |

Expected closure shape:

```text
featurelifted/
  ...
```

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | Tokens | Notes |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

Target pass rate for strong agents: **35–55%** per hard task (hard subset aggregate **35–45%** when calibrating).

## Go / No-Go Criteria

- Oracle and Copy-All are clearly separated on ExtractionRatio.
- At least three module probes verified.
- Adds entanglement or discrimination not covered by existing pilot tasks.
- Agent pass rate > 70% → strengthen hidden tests or narrow public hints.
- Agent pass rate < 20% → widen public guidance or reduce closure scope.
