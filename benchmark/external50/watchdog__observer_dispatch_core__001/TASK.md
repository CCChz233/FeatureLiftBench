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
  - `Observer.schedule(event_handler: FileSystemEventHandler, path: str, recursive: bool = False)`
  - `Observer.start() -> None`
  - `Observer.stop() -> None`
  - `Observer.join(timeout: float | None = None) -> None`
- `FileSystemEventHandler` class must be importable
- `FileCreatedEvent` class must be importable
- `FileModifiedEvent` class must be importable
- `FileDeletedEvent` class must be importable

## Required Behavior

- After a FileSystemEventHandler is scheduled on a directory and Observer is started, creating a file causes the handler's on_created callback to receive an event whose `src_path` identifies that file; stop() followed by join(timeout=...) shuts the observer down.
- While an Observer watches a temporary directory, creating, rewriting, and deleting a file dispatches filesystem events through FileSystemEventHandler.on_any_event, so the handler records at least one event from the change sequence.
- FileCreatedEvent, FileModifiedEvent, and FileDeletedEvent are importable class objects that can identify the corresponding filesystem event categories.
- Observer accepts a polling timeout, watches local filesystem state without network access, and detects changes made after start() within the bounded test wait.
- The package exposes Observer/FileSystemEventHandler/FileCreatedEvent/FileModifiedEvent/FileDeletedEvent with the kinds listed in this contract.
- Scanning every Python file in the submitted package finds no `import watchdog` or `from watchdog ...` statement.

## Constraints

- Forbidden imports: `watchdog`.
- Do not implement inotify-specific flags.
- Do not implement watchmedo CLI.
- Do not implement original watchdog import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — After a FileSystemEventHandler is scheduled on a directory and Observer is started, creating a file causes the handler's on_created callback to receive an event whose `src_path` identifies that file; stop() followed by join(timeout=...) shuts the observer down.
- **B002** — While an Observer watches a temporary directory, creating, rewriting, and deleting a file dispatches filesystem events through FileSystemEventHandler.on_any_event, so the handler records at least one event from the change sequence.
- **B003** — FileCreatedEvent, FileModifiedEvent, and FileDeletedEvent are importable class objects that can identify the corresponding filesystem event categories.
- **B004** — Observer accepts a polling timeout, watches local filesystem state without network access, and detects changes made after start() within the bounded test wait.
- **B005** — The package exposes Observer/FileSystemEventHandler/FileCreatedEvent/FileModifiedEvent/FileDeletedEvent with the kinds listed in this contract.
- **B006** — Scanning every Python file in the submitted package finds no `import watchdog` or `from watchdog ...` statement.
<!-- featureliftbench:behavior-clauses:end -->
