# FeatureLift Task: Cron trigger next-fire-time state

Extract cron next-fire-time logic into `featurelifted`.

## Target API

```python
from featurelifted import CronTrigger
```

## Required Behavior

- `CronTrigger` parses minute/hour/day fields including `*`, ranges, and `*/step` forms.
- `get_next_fire_time` returns the next matching datetime after `now`, respecting `start_time` and `end_time`.

## Constraints

- Forbidden imports: `apscheduler`.
- No scheduler stores, executors, or subprocesses.
