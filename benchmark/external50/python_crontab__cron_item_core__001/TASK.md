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
  - `CronSlices.is_valid` callable must exist
  - `CronSlices.setall` callable must exist
  - `CronSlices.render` callable must exist
  - `CronSlices.special` attribute must exist on instances
- `CronSlices.is_valid` callable must exist
- `CronItem` class must be importable
  - `CronItem.render` callable must exist
  - `CronItem.is_valid` callable must exist
  - `CronItem.is_enabled` callable must exist
- `CronItem.render` callable must exist
- `CronItem.is_valid` callable must exist

## Required Behavior

- The extracted feature must support this observable behavior: CronSlices parse/render/is_valid. Required observable cases include cron slices valid; slices setall.
- The extracted feature must support this observable behavior: CronItem constructor render/is_valid. Required observable cases include cron item from line; cron item invalid line.
- The extracted feature must support this observable behavior: special @reboot slices. Required observable cases include special reboot.
- No OS crontab file access is required.
- The package exposes CronSlices/CronItem with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: crontab.

## Constraints

- Forbidden imports: `crontab`.
- Do not implement OS crontab file IO.
- Do not implement original crontab import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: CronSlices parse/render/is_valid. Required observable cases include cron slices valid; slices setall.
- **B002** — The extracted feature must support this observable behavior: CronItem constructor render/is_valid. Required observable cases include cron item from line; cron item invalid line.
- **B003** — The extracted feature must support this observable behavior: special @reboot slices. Required observable cases include special reboot.
- **B004** — No OS crontab file access is required.
- **B005** — The package exposes CronSlices/CronItem with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: crontab.
<!-- featureliftbench:behavior-clauses:end -->
