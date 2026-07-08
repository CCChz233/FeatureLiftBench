# Task Design: tenacity__retry_state_core__hard3_001

Status: agent-calibrated

## Why This Task

Extract synchronous Tenacity retry state machine with composable stop/wait/retry policies.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Wait strategies | `featurelifted/_wait.py` | `test_wait_chain_requires_at_least_one_strategy` |
| Retry engine | `featurelifted/_engine.py` | `test_reraise_surfaces_last_exception` |
| Core state | `featurelifted/_core.py` | `test_before_sleep_observes_retry_state` |
