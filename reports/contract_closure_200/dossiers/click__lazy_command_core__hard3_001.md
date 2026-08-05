# click__lazy_command_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `5/9`

## Required API

- `featurelifted.LazyCommandCollection` (class) `(sources: 'dict[str, Callable[[], Command]]', *, envvar: 'str | None' = None) -> 'None'`
- `featurelifted.LazyCommandCollection.get_command` (method) `(self, name: 'str') -> 'Command | None'`
- `featurelifted.LazyCommandCollection.resolve` (method) `(self, argv: 'list[str]') -> 'tuple[Context, Command, list[str]]'`
- `featurelifted.Command` (class) `(name: 'str', callback: 'Callable[..., Any] | None' = None) -> 'None'`
- `featurelifted.UsageError` (exception)

## Public Behaviors

- **B001**: When a command name is requested, LazyCommandCollection loads only the source that supplies that command and caches the resolved command.
- **B002**: When a context is created, collection defaults and envvar settings are propagated to command resolution without eagerly loading unrelated commands.
- **B003**: When resolve receives argv, it returns the resolved Context, Command, and remaining arguments and raises UsageError for unknown commands.
- **B004**: The package exposes the required task API paths `featurelifted.LazyCommandCollection`, `featurelifted.LazyCommandCollection.get_command`, `featurelifted.LazyCommandCollection.resolve`, `featurelifted.Command`, `featurelifted.UsageError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_lazy_command_invoke`

- mapping: `B001`
- API: `featurelifted.Command, featurelifted.LazyCommandCollection`
- risk: `none`
- A001 `assert` L10: `collection.invoke(['echo', 'hi']) == ['hi']`

### `hidden_tests/test_hidden_contract.py::test_envvar_default_map`

- mapping: `B002`
- API: `featurelifted.Command, featurelifted.LazyCommandCollection`
- risk: `environment_state`
- A001 `assert` L13: `ctx.default_map['echo']['verbose'] is True`

### `hidden_tests/test_hidden_contract.py::test_missing_command_raises`

- mapping: `B001, B003`
- API: `featurelifted.LazyCommandCollection, featurelifted.UsageError`
- risk: `exact_error_text, exception_semantics`
- A001 `raises` L18: `pytest.raises(UsageError, match='no such command')`

### `hidden_tests/test_hidden_contract.py::test_command_is_cached`

- mapping: `B001, B003`
- API: `featurelifted.Command, featurelifted.LazyCommandCollection`
- risk: `state_mutation`
- A001 `assert` L34: `calls == [1]`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.Command, featurelifted.LazyCommandCollection, featurelifted.UsageError`
- risk: `none`
- A001 `assert` L11: `isinstance(LazyCommandCollection, type)`
- A002 `assert` L12: `hasattr(LazyCommandCollection, 'get_command')`
- A003 `assert` L13: `hasattr(LazyCommandCollection, 'resolve')`
- A004 `assert` L14: `isinstance(Command, type)`
- A005 `assert` L15: `issubclass(UsageError, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `click`
- source entrypoints: `click.core.LazyCommandCollection`
- oracle source files: `repo/src/click/core.py`
- runtime dependencies: `none`
- oracle notes: Lazy command collection subset without full CLI.
