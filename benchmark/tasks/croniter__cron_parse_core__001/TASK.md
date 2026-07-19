# FeatureLift Task: Cron expression parse and next/prev iteration

Extract croniter cron parsing with field expansion and naive datetime next/prev iteration without original croniter import.

## Target API

- Import: `import featurelifted; from featurelifted import croniter, datetime_to_timestamp, CroniterBadCronError, CroniterBadDateError, CroniterNotAlphaError`
- Callable: `featurelifted.croniter`
- Signature: `croniter(expr_format, start_time=None, ret_type=...)`

## Excluded Behavior

- croniter_range generator
- hash/random H() field expansion
- match_range and is_valid helpers
- original croniter import at runtime
- timezone/DST-aware scheduling (tests use naive datetimes only)

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `croniter`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — parse standard 5-field cron expressions
- **B002** — compute next matching naive datetime from a base time
- **B003** — compute previous matching naive datetime from a base time
- **B004** — step and range field expansion (e.g. */15, 9-17)
- **B005** — reject invalid field values with CroniterBadCronError
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: croniter
<!-- featureliftbench:behavior-clauses:end -->
