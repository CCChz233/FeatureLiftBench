# decorator__signature_preserving_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `4/10`

## Required API

- `featurelifted.decorate` (function) `(func, caller)`
- `featurelifted.decorator` (function) `(caller, func=None)`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: caller receives the original function before bound arguments. Required observable cases include metadata signature and call order; invalid calls follow original signature; async caller and wrapped.
- **B002**: The extracted feature must support this observable behavior: decorated call enforces the original function signature. Required observable cases include metadata signature and call order; invalid calls follow original signature; async caller and wrapped.
- **B003**: The extracted feature must support this observable behavior: name, docstring, module, annotations, wrapped, and inspect.signature are preserved. Required observable cases include metadata signature and call order; invalid calls follow original signature; async caller and wrapped.
- **B004**: The extracted feature must support this observable behavior: async callers and coroutine functions remain awaitable. Required observable cases include metadata signature and call order; invalid calls follow original signature; async caller and wrapped.
- **B005**: The package exposes the required task API paths `featurelifted.decorate`, `featurelifted.decorator` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_metadata_signature_and_call_order`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.decorator`
- risk: `exact_error_text, ordering_semantics`
- A001 `assert` L12: `add(2, b=3) == 10`
- A002 `assert` L13: `str(inspect.signature(add)) == '(a: int, b: int = 1) -> int'`
- A003 `assert` L14: `add.__name__ == 'add' and add.__doc__ == 'add values'`
- A004 `assert` L15: `calls == [((2,), {'b': 3})]`

### `hidden_tests/test_hidden_contract.py::test_invalid_calls_follow_original_signature`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.decorator`
- risk: `exception_semantics`
- A001 `raises` L7: `pytest.raises(TypeError)`

### `hidden_tests/test_hidden_contract.py::test_async_caller_and_wrapped`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.decorate`
- risk: `none`
- A001 `assert` L13: `inspect.iscoroutinefunction(wrapped)`
- A002 `assert` L14: `wrapped.__wrapped__ is base`
- A003 `assert` L15: `asyncio.run(wrapped(3)) == 7`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.decorate, featurelifted.decorator`
- risk: `none`
- A001 `assert` L10: `callable(decorate)`
- A002 `assert` L11: `callable(decorator)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `decorator`
- source entrypoints: `decorator.decorator, decorator.decorate`
- oracle source files: `decorator.decorator, decorator.decorate`
- runtime dependencies: `none`
- oracle notes: Entrypoints are maintainer-private provenance and are never Agent-visible in Main.
- behavior contract lacks a completed review_status
