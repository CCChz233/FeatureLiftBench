# watchdog__observer_dispatch_core__001

- release: `external50`
- lift: `Composite`
- coupling: `resource_coupling`
- strict validation: `PASS`
- tests/assertions: `5/15`

## Required API

- `featurelifted.Observer` (class)
- `featurelifted.Observer.schedule` (method)
- `featurelifted.Observer.start` (method)
- `featurelifted.Observer.stop` (method)
- `featurelifted.Observer.join` (method)
- `featurelifted.FileSystemEventHandler` (class)
- `featurelifted.FileCreatedEvent` (class)
- `featurelifted.FileModifiedEvent` (class)
- `featurelifted.FileDeletedEvent` (class)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: Observer schedule/start/stop delivers create events to FileSystemEventHandler. Required observable cases include observer create event.
- **B002**: The extracted feature must support this observable behavior: modify/delete callbacks fire for temp-dir file changes. Required observable cases include modify and delete.
- **B003**: The extracted feature must support this observable behavior: FileCreatedEvent/FileModifiedEvent/FileDeletedEvent types exist. Required observable cases include event types exist.
- **B004**: Observer is the polling implementation for deterministic offline tests.
- **B005**: The package exposes Observer/FileSystemEventHandler/FileCreatedEvent/FileModifiedEvent/FileDeletedEvent with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: watchdog.

## Tests

### `public_tests/test_public_api.py::test_observer_create_event`

- mapping: `B001`
- API: `featurelifted.Observer`
- risk: `filesystem_resource, time_or_randomness`
- A001 `assert` L28: `any((str(target) in p or p.endswith('a.txt') for p in handler.created))`

### `hidden_tests/test_hidden_behavior.py::test_modify_and_delete`

- mapping: `B001, B003, B004`
- API: `featurelifted.Observer`
- risk: `filesystem_resource, time_or_randomness`
- A001 `assert` L39: `handler.events`

### `hidden_tests/test_hidden_behavior.py::test_event_types_exist`

- mapping: `B002`
- API: `featurelifted.FileCreatedEvent, featurelifted.FileDeletedEvent, featurelifted.FileModifiedEvent`
- risk: `none`
- A001 `assert` L46: `FileCreatedEvent is not None`
- A002 `assert` L47: `FileModifiedEvent is not None`
- A003 `assert` L48: `FileDeletedEvent is not None`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L57: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.Observer, featurelifted.Observer.join, featurelifted.Observer.schedule, featurelifted.Observer.start, featurelifted.Observer.stop`
- risk: `none`
- A001 `assert` L5: `hasattr(featurelifted, 'FileCreatedEvent')`
- A002 `assert` L6: `hasattr(featurelifted, 'FileDeletedEvent')`
- A003 `assert` L7: `hasattr(featurelifted, 'FileModifiedEvent')`
- A004 `assert` L8: `hasattr(featurelifted, 'FileSystemEventHandler')`
- A005 `assert` L9: `hasattr(featurelifted, 'Observer')`
- A006 `assert` L10: `callable(featurelifted.Observer.schedule)`
- A007 `assert` L11: `callable(featurelifted.Observer.start)`
- A008 `assert` L12: `callable(featurelifted.Observer.stop)`
- A009 `assert` L13: `callable(featurelifted.Observer.join)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `watchdog`
- source entrypoints: `none`
- oracle source files: `src/watchdog/observers/polling.py, src/watchdog/events.py`
- runtime dependencies: `none`
- oracle notes: PollingObserver exported as Observer for deterministic offline tests.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
