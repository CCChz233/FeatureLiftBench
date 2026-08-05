# freezegun__freeze_time_core__001

- release: `external50`
- lift: `Adapted`
- coupling: `config_environment_coupling`
- strict validation: `PASS`
- tests/assertions: `7/21`

## Required API

- `featurelifted.freeze_time` (function) `(time_to_freeze=None, tick: bool = False, ...)`
- `featurelifted.FrozenDateTimeFactory` (class)
- `featurelifted.FrozenDateTimeFactory.tick` (method)
- `featurelifted.FrozenDateTimeFactory.move_to` (method)
- `featurelifted.TickingDateTimeFactory` (class)
- `featurelifted.TickingDateTimeFactory.tick` (method)
- `featurelifted.TickingDateTimeFactory.move_to` (method)
- `featurelifted.StepTickTimeFactory` (class)
- `featurelifted.StepTickTimeFactory.tick` (method)
- `featurelifted.StepTickTimeFactory.move_to` (method)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: freeze_time context manager and decorator. Required observable cases include freeze context manager; freeze decorator; unfrozen after context.
- **B002**: The extracted feature must support this observable behavior: tick and move_to advance frozen time. Required observable cases include tick moves time; move to.
- **B003**: Real clock resumes after the freeze context exits.
- **B004**: python-dateutil is the only allowed third-party dependency.
- **B005**: The package exposes freeze_time with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: freezegun.

## Tests

### `public_tests/test_public_api.py::test_freeze_context_manager`

- mapping: `B001`
- API: `featurelifted.freeze_time`
- risk: `time_or_randomness`
- A001 `assert` L10: `datetime.now().year == 2020`
- A002 `assert` L11: `datetime.now().month == 1`
- A003 `assert` L12: `datetime.now().day == 15`

### `public_tests/test_public_api.py::test_freeze_decorator`

- mapping: `B002`
- API: `featurelifted.freeze_time`
- risk: `time_or_randomness`
- A001 `assert` L20: `stamped() == 2019`

### `public_tests/test_public_api.py::test_unfrozen_after_context`

- mapping: `B003`
- API: `featurelifted.freeze_time`
- risk: `time_or_randomness`
- A001 `assert` L27: `datetime.now().year == real_year`
- A002 `assert` L26: `datetime.now().year == 2001`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L13: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_hidden_behavior.py::test_tick_moves_time`

- mapping: `B001, B002, B004`
- API: `featurelifted.freeze_time`
- risk: `time_or_randomness`
- A001 `assert` L26: `t1 > t0`
- A002 `assert` L27: `t1.hour == 1`

### `hidden_tests/test_hidden_behavior.py::test_move_to`

- mapping: `B003`
- API: `featurelifted.freeze_time`
- risk: `time_or_randomness`
- A001 `assert` L33: `datetime.now().year == 2021`
- A002 `assert` L34: `datetime.now().month == 12`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.FrozenDateTimeFactory, featurelifted.FrozenDateTimeFactory.move_to, featurelifted.FrozenDateTimeFactory.tick, featurelifted.StepTickTimeFactory, featurelifted.StepTickTimeFactory.move_to, featurelifted.StepTickTimeFactory.tick, featurelifted.TickingDateTimeFactory, featurelifted.TickingDateTimeFactory.move_to, featurelifted.TickingDateTimeFactory.tick`
- risk: `none`
- A001 `assert` L5: `hasattr(featurelifted, 'FrozenDateTimeFactory')`
- A002 `assert` L6: `hasattr(featurelifted, 'StepTickTimeFactory')`
- A003 `assert` L7: `hasattr(featurelifted, 'TickingDateTimeFactory')`
- A004 `assert` L8: `hasattr(featurelifted, 'freeze_time')`
- A005 `assert` L9: `callable(featurelifted.FrozenDateTimeFactory.tick)`
- A006 `assert` L10: `callable(featurelifted.FrozenDateTimeFactory.move_to)`
- A007 `assert` L11: `callable(featurelifted.TickingDateTimeFactory.tick)`
- A008 `assert` L12: `callable(featurelifted.TickingDateTimeFactory.move_to)`
- A009 `assert` L13: `callable(featurelifted.StepTickTimeFactory.tick)`
- A010 `assert` L14: `callable(featurelifted.StepTickTimeFactory.move_to)`

## Dependency / Oracle Evidence

- allowed dependencies: `python-dateutil, six`
- forbidden imports: `freezegun`
- source entrypoints: `none`
- oracle source files: `freezegun/api.py, freezegun/__init__.py`
- runtime dependencies: `python-dateutil, six`
- oracle notes: Adapted freeze_time context manager and decorator.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
