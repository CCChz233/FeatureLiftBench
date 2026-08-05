# Contract V2 P0: freezegun__freeze_time_core__001

- release: `external50`
- lift: `Adapted`
- coupling: `config_environment_coupling`
- strict validation: `PASS`
- tests/assertions: `8/23`

## Required API

- `featurelifted.freeze_time` (function) `(time_to_freeze=None, tz_offset=0, ignore=None, tick: bool = False, as_arg: bool = False, as_kwarg: str = '', auto_tick_seconds: float = 0, real_asyncio: bool = False) -> context manager/decorator yielding FrozenDateTimeFactory | TickingDateTimeFactory | StepTickTimeFactory`
- `featurelifted.FrozenDateTimeFactory` (class) `(time_to_freeze: datetime.datetime)`
- `featurelifted.FrozenDateTimeFactory.tick` (method) `(self, delta: Union[datetime.timedelta, float] = datetime.timedelta(seconds=1)) -> datetime.datetime`
- `featurelifted.FrozenDateTimeFactory.move_to` (method) `(self, target_datetime: Union[str, datetime.datetime, datetime.date, datetime.timedelta, function, Callable[[], Union[str, datetime.datetime, datetime.date, datetime.timedelta]], Iterator[datetime.datetime]]) -> None`
- `featurelifted.TickingDateTimeFactory` (class) `(time_to_freeze: datetime.datetime, start: datetime.datetime)`
- `featurelifted.TickingDateTimeFactory.tick` (method) `(self, delta: Union[datetime.timedelta, float] = datetime.timedelta(seconds=1)) -> datetime.datetime`
- `featurelifted.TickingDateTimeFactory.move_to` (method) `(self, target_datetime: Union[str, datetime.datetime, datetime.date, datetime.timedelta, function, Callable[[], Union[str, datetime.datetime, datetime.date, datetime.timedelta]], Iterator[datetime.datetime]]) -> None`
- `featurelifted.StepTickTimeFactory` (class) `(time_to_freeze: datetime.datetime, step_width: float)`
- `featurelifted.StepTickTimeFactory.tick` (method) `(self, delta: Union[datetime.timedelta, float, NoneType] = None) -> datetime.datetime`
- `featurelifted.StepTickTimeFactory.move_to` (method) `(self, target_datetime: Union[str, datetime.datetime, datetime.date, datetime.timedelta, function, Callable[[], Union[str, datetime.datetime, datetime.date, datetime.timedelta]], Iterator[datetime.datetime]]) -> None`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: freeze_time context manager and decorator. Required observable cases include freeze context manager; freeze decorator; unfrozen after context.
- **B002**: The extracted feature must support this observable behavior: tick and move_to advance frozen time. Required observable cases include tick moves time; move to.
- **B003**: Real clock resumes after the freeze context exits.
- **B004**: python-dateutil and six are the only allowed third-party runtime dependencies.
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

- mapping: `B001`
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

- mapping: `B004, B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L16: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_hidden_behavior.py::test_tick_moves_time`

- mapping: `B002`
- API: `featurelifted.freeze_time`
- risk: `time_or_randomness`
- A001 `assert` L24: `t1 > t0`
- A002 `assert` L25: `t1.hour == 1`

### `hidden_tests/test_hidden_behavior.py::test_move_to`

- mapping: `B002`
- API: `featurelifted.freeze_time`
- risk: `time_or_randomness`
- A001 `assert` L31: `datetime.now().year == 2021`
- A002 `assert` L32: `datetime.now().month == 12`

### `hidden_tests/test_hidden_behavior.py::test_unfrozen_after_hidden_context`

- mapping: `B001, B003`
- API: `featurelifted.freeze_time`
- risk: `time_or_randomness`
- A001 `assert` L39: `datetime.now().year == real_year`
- A002 `assert` L38: `datetime.now().year == 2001`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.FrozenDateTimeFactory, featurelifted.StepTickTimeFactory, featurelifted.TickingDateTimeFactory, featurelifted.freeze_time`
- risk: `none`
- A001 `assert` L12: `callable(freeze_time)`
- A002 `assert` L13: `isinstance(FrozenDateTimeFactory, type)`
- A003 `assert` L14: `hasattr(FrozenDateTimeFactory, 'tick')`
- A004 `assert` L15: `hasattr(FrozenDateTimeFactory, 'move_to')`
- A005 `assert` L16: `isinstance(TickingDateTimeFactory, type)`
- A006 `assert` L17: `hasattr(TickingDateTimeFactory, 'tick')`
- A007 `assert` L18: `hasattr(TickingDateTimeFactory, 'move_to')`
- A008 `assert` L19: `isinstance(StepTickTimeFactory, type)`
- A009 `assert` L20: `hasattr(StepTickTimeFactory, 'tick')`
- A010 `assert` L21: `hasattr(StepTickTimeFactory, 'move_to')`

## Dependency / Oracle Evidence

- allowed dependencies: `python-dateutil, six`
- forbidden imports: `freezegun`
- source entrypoints: `none`
- oracle source files: `freezegun/api.py, freezegun/__init__.py`
- runtime dependencies: `python-dateutil, six`
- oracle notes: Adapted freeze_time context manager and decorator.
