# FeatureLift Task: huey task schedule

Extract a task-scoped subset of `huey` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    crontab,
    MemoryHuey,
)
```

## Required API Details

- `MemoryHuey` class must be importable
  - `MemoryHuey.task` callable must exist
  - `MemoryHuey.pending_count` callable must exist
  - `MemoryHuey.flush` callable must exist
- `crontab` callable must exist

## Required Behavior

- The extracted feature must support this observable behavior: enqueue tasks and read results via result.get after execute. Required observable cases include task enqueue and result.
- The extracted feature must support this observable behavior: crontab schedule helper. Required observable cases include crontab helper.
- The extracted feature must support this observable behavior: multiple tasks and flush clears queue. Required observable cases include multiple tasks; flush clears queue.
- MemoryHuey is the only broker backend required.
- The package exposes MemoryHuey and crontab with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: huey.

## Constraints

- Forbidden imports: `huey`.
- Do not implement RedisHuey.
- Do not implement consumer process.
- Do not implement original huey import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: enqueue tasks and read results via result.get after execute. Required observable cases include task enqueue and result.
- **B002** — The extracted feature must support this observable behavior: crontab schedule helper. Required observable cases include crontab helper.
- **B003** — The extracted feature must support this observable behavior: multiple tasks and flush clears queue. Required observable cases include multiple tasks; flush clears queue.
- **B004** — MemoryHuey is the only broker backend required.
- **B005** — The package exposes MemoryHuey and crontab with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: huey.
<!-- featureliftbench:behavior-clauses:end -->
