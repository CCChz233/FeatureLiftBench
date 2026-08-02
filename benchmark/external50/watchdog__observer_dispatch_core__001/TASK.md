# FeatureLift Task: watchdog observer dispatch

Extract a task-scoped subset of `watchdog` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    FileCreatedEvent,
    FileDeletedEvent,
    FileModifiedEvent,
    FileSystemEventHandler,
    Observer,
)
```

## Required API Details

- `Observer` class must be importable
  - `Observer.schedule` callable must exist
  - `Observer.start` callable must exist
  - `Observer.stop` callable must exist
  - `Observer.join` callable must exist
- `FileSystemEventHandler` class must be importable
- `FileCreatedEvent` class must be importable
- `FileModifiedEvent` class must be importable
- `FileDeletedEvent` class must be importable

## Required Behavior

- The extracted feature must support this observable behavior: Observer schedule/start/stop delivers create events to FileSystemEventHandler. Required observable cases include observer create event.
- The extracted feature must support this observable behavior: modify/delete callbacks fire for temp-dir file changes. Required observable cases include modify and delete.
- The extracted feature must support this observable behavior: FileCreatedEvent/FileModifiedEvent/FileDeletedEvent types exist. Required observable cases include event types exist.
- Observer is the polling implementation for deterministic offline tests.
- The package exposes Observer/FileSystemEventHandler/FileCreatedEvent/FileModifiedEvent/FileDeletedEvent with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: watchdog.

## Constraints

- Forbidden imports: `watchdog`.
- Do not implement inotify-specific flags.
- Do not implement watchmedo CLI.
- Do not implement original watchdog import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: Observer schedule/start/stop delivers create events to FileSystemEventHandler. Required observable cases include observer create event.
- **B002** — The extracted feature must support this observable behavior: modify/delete callbacks fire for temp-dir file changes. Required observable cases include modify and delete.
- **B003** — The extracted feature must support this observable behavior: FileCreatedEvent/FileModifiedEvent/FileDeletedEvent types exist. Required observable cases include event types exist.
- **B004** — Observer is the polling implementation for deterministic offline tests.
- **B005** — The package exposes Observer/FileSystemEventHandler/FileCreatedEvent/FileModifiedEvent/FileDeletedEvent with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: watchdog.
<!-- featureliftbench:behavior-clauses:end -->
