# FeatureLift Task: python-crontab cron item

Extract a task-scoped subset of `python-crontab` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    CronItem,
    CronSlices,
)
```

## Required API Details

- `CronSlices` class must be importable
  - `CronSlices.is_valid(value: str) -> bool`
  - `CronSlices.setall(*values: str) -> None`
  - `CronSlices.render() -> str`
  - `CronSlices.special` attribute must exist on instances
- `CronSlices.is_valid(value: str) -> bool`
- `CronItem` class must be importable
  - `CronItem.render() -> str`
  - `CronItem.is_valid() -> bool`
  - `CronItem.is_enabled() -> bool`
- `CronItem.render() -> str`
- `CronItem.is_valid() -> bool`

## Required Behavior

- CronSlices.is_valid returns true for a five-field expression such as `* * * * *` and false for malformed text; constructing CronSlices from a valid expression and calling render() returns its cron fields.
- Constructing CronItem from a valid five-field schedule followed by a command produces an item whose is_valid() and is_enabled() return true and whose render() output contains the command; these three methods are callable on CronItem.
- Constructing CronSlices with `@reboot` preserves that special schedule so either render() contains `@reboot` or the `special` attribute equals `@reboot`.
- After constructing empty CronSlices and calling setall("0", "12", "*", "*", "1"), render() contains the configured minute and hour values without requiring OS crontab access.
- The package exposes CronSlices/CronItem with the kinds listed in this contract.
- Scanning every Python file in the submitted package finds no `import crontab` or `from crontab ...` statement.

## Constraints

- Forbidden imports: `crontab`.
- Do not implement OS crontab file IO.
- Do not implement original crontab import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — CronSlices.is_valid returns true for a five-field expression such as `* * * * *` and false for malformed text; constructing CronSlices from a valid expression and calling render() returns its cron fields.
- **B002** — Constructing CronItem from a valid five-field schedule followed by a command produces an item whose is_valid() and is_enabled() return true and whose render() output contains the command; these three methods are callable on CronItem.
- **B003** — Constructing CronSlices with `@reboot` preserves that special schedule so either render() contains `@reboot` or the `special` attribute equals `@reboot`.
- **B004** — After constructing empty CronSlices and calling setall("0", "12", "*", "*", "1"), render() contains the configured minute and hour values without requiring OS crontab access.
- **B005** — The package exposes CronSlices/CronItem with the kinds listed in this contract.
- **B006** — Scanning every Python file in the submitted package finds no `import crontab` or `from crontab ...` statement.
<!-- featureliftbench:behavior-clauses:end -->
