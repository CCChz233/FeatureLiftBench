# Task Design: `<task_id>`

> Machine-readable task spec: [TASK_FORMAT.md](../TASK_FORMAT.md). This file is the human design note.

Status: draft | oracle-verified | agent-calibrated

## Why This Task

Explain why this task belongs in FeatureLiftBench and what discrimination it provides (functional vs decoupling).

## Practical reuse（必填）

Answer in plain language (see [EXPANSION.md](../EXPANSION.md)):

1. **Reuse module** — If decoupling succeeds, what real-world module does `featurelifted` represent? (e.g. SQL parse/format core, config bootstrap, plugin registry API)
2. **Who imports it** — In what downstream scenario would a team install or copy this package alone?
3. **Why not copy-all** — Why is a compact closure more realistic than vendoring the whole `repo/`?

For **curated `vibe_app`** tasks, state explicitly that the source simulates vibe-coded / legacy clutter, not a published PyPI library.

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

Target pass rate for strong agents: **35–55%** per hard task is a historical calibration guide; **leaderboard functional pass may be re-evaluated** (see [EXPANSION.md](../EXPANSION.md)).

## Go / No-Go Criteria

- **Practical reuse** section completed; reuse story is credible for a hard-task maintainer review.
- Oracle and Copy-All are clearly separated on ExtractionRatio.
- At least three module probes verified.
- Adds entanglement or discrimination not covered by existing tasks (prefer **replace** over growing past 50 hard — [EXPANSION.md](../EXPANSION.md)).
- Agent pass rate > 70% with copy-heavy submissions → strengthen hidden tests or narrow public hints before accepting the task.
- Agent pass rate < 20% → widen public guidance or reduce closure scope; confirm the task is still a fair reuse slice.

Per-task agent calibration target **35–55%** is a historical design guide. **Leaderboard functional pass may be re-evaluated** across model generations; discrimination via `final_score` and extraction tiers remains required in reports.
