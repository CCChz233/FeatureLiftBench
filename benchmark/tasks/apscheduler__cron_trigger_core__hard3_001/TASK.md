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

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — cron field parsing subset
- **B002** — next fire time iteration
- **B003** — end_time boundary
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: apscheduler
<!-- featureliftbench:behavior-clauses:end -->
