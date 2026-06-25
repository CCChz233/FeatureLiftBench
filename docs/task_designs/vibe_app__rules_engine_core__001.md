# Task Design: vibe_app__rules_engine_core__001

Status: oracle-verified

## Why This Task

Extract canonical rules evaluation from a vibe-coded shop app where duplicate helpers in `utils.py` hide the correct priority-ordered engine.

## Source

| Field | Value |
| --- | --- |
| Source repo | `sources/vibe_app/` |
| Commit | curated |
| License | MIT |
| Difficulty | hard |
| Tags | extreme, multi-task-repo, legacy_vibe_clutter |

## Output API

```python
from featurelifted import Rule, RulesEngine, evaluate_rules
```

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Conditions | `rules_engine/conditions.py` | `test_contains_operator_matches_list_membership` |
| Actions | `rules_engine/actions.py` | `test_inc_action_accumulates_counter` |
| Engine orchestration | `rules_engine/engine.py` | `test_rule_applies_set_action_when_condition_matches` (public) |
