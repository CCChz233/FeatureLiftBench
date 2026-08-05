# sqlalchemy__event_dispatch_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `4/8`

## Required API

- `featurelifted.listen` (function) `(target: 'type', identifier: 'str', fn: 'Callable', once: 'bool' = False, propagate: 'bool' = False, named: 'bool' = False) -> 'None'`
- `featurelifted.remove` (function) `(target: 'type', identifier: 'str', fn: 'Callable') -> 'None'`
- `featurelifted.dispatch` (function) `(target: 'type', identifier: 'str', *args, **kwargs) -> 'None'`
- `featurelifted.EventTarget` (class) `()`

## Public Behaviors

- **B001**: `listen` registers listeners for `(target, identifier)` pairs.
- **B002**: `dispatch` invokes active listeners; `once=True` listeners run at most once.
- **B003**: `remove` during dispatch must not break in-flight dispatch.
- **B004**: `propagate=True` also registers on subclasses.
- **B005**: `named=True` invokes listeners with keyword arguments.
- **B006**: The package exposes the required task API paths `featurelifted.listen`, `featurelifted.remove`, `featurelifted.dispatch`, `featurelifted.EventTarget` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_dispatch_invokes_listener`

- mapping: `B001, B002`
- API: `featurelifted.dispatch, featurelifted.listen`
- risk: `none`
- A001 `assert` L13: `seen == [1]`

### `hidden_tests/test_hidden_contract.py::test_once_and_remove_during_dispatch_and_propagation`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.dispatch, featurelifted.listen, featurelifted.remove`
- risk: `none`
- A001 `assert` L27: `calls == ['during', 'once']`
- A002 `assert` L32: `child_calls == [1]`

### `hidden_tests/test_hidden_contract.py::test_named_kwargs_dispatch`

- mapping: `B005`
- API: `featurelifted.dispatch, featurelifted.listen`
- risk: `none`
- A001 `assert` L39: `seen == {'value': 7}`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.EventTarget, featurelifted.dispatch, featurelifted.listen, featurelifted.remove`
- risk: `none`
- A001 `assert` L12: `callable(listen)`
- A002 `assert` L13: `callable(remove)`
- A003 `assert` L14: `callable(dispatch)`
- A004 `assert` L15: `isinstance(EventTarget, type)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `sqlalchemy`
- source entrypoints: `sqlalchemy.event.listen, sqlalchemy.event.remove`
- oracle source files: `repo/lib/sqlalchemy/event/api.py, repo/lib/sqlalchemy/event/registry.py, repo/lib/sqlalchemy/event/base.py`
- runtime dependencies: `none`
- oracle notes: Event dispatch subset without ORM/engine/database access.
