# Task Design: stevedore__extension_manager_core__hard3_001

Status: agent-calibrated

## Why This Task

Extract Stevedore-style extension manager discovery/loading with callback, duplicate-name, and map semantics.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Named manager | `featurelifted/_named.py` | `test_named_extension_manager_filters_reports_missing_and_orders_names` |
| Conflict policy | `featurelifted/_conflicts.py` | `test_duplicate_names_can_raise_multiple_matches` |
| Extension core | `featurelifted/_extension.py` | `test_load_failure_callback_gets_manager_entrypoint_and_exception` |
