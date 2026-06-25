# Task Design: pluggy__hook_specs_core__001

Status: oracle-verified

## Why This Task

Extract pluggy hookspec validation and historic replay behavior, complementing hook_call_order with spec-first discrimination.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Hook specs | `_hooks.py` | `test_unknown_hook_argument_rejected` (public) |
| Manager validation | `_manager.py` | `test_check_pending_requires_optional_for_unknown_hooks` (public) |
| Hook callers | `_callers.py` | `test_historic_hook_replays_for_late_registration` |
