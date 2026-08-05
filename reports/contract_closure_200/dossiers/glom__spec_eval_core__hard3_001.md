# glom__spec_eval_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `4/9`

## Required API

- `featurelifted.glom` (function) `(target, spec, default=None)`
- `featurelifted.T` (object)
- `featurelifted.Coalesce` (class) `(specs: 'list[Any]', default: 'Any' = None) -> None`
- `featurelifted.PathAccessError` (exception)

## Public Behaviors

- **B001**: `glom` evaluates dict/list/tuple specs, dotted path strings, callables, `T`, and `Coalesce`.
- **B002**: `Coalesce` returns the first successful child spec or a configured default.
- **B003**: When a T expression is evaluated, attribute and item traversal start from the current target and compose in expression order.
- **B004**: When dotted-path or T traversal cannot access a requested component, glom raises PathAccessError unless a declared default handles the failure.
- **B005**: The package exposes the required task API paths `featurelifted.glom`, `featurelifted.T`, `featurelifted.Coalesce`, `featurelifted.PathAccessError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_glom_path_and_t`

- mapping: `B001`
- API: `featurelifted.T, featurelifted.glom`
- risk: `none`
- A001 `assert` L7: `glom(target, 'user.name') == 'Ada'`
- A002 `assert` L8: `glom(target, T) is target`

### `hidden_tests/test_hidden_contract.py::test_coalesce_and_default`

- mapping: `B002`
- API: `featurelifted.Coalesce, featurelifted.glom`
- risk: `none`
- A001 `assert` L9: `glom(target, Coalesce(['missing', 'a'], default=0)) == 1`
- A002 `assert` L10: `glom(target, 'missing', default='fallback') == 'fallback'`

### `hidden_tests/test_hidden_contract.py::test_nested_path_error`

- mapping: `B001, B003, B004`
- API: `featurelifted.PathAccessError, featurelifted.glom`
- risk: `exception_semantics`
- A001 `raises` L14: `pytest.raises(PathAccessError)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.Coalesce, featurelifted.PathAccessError, featurelifted.T, featurelifted.glom`
- risk: `none`
- A001 `assert` L12: `callable(glom)`
- A002 `assert` L13: `T is not None`
- A003 `assert` L14: `isinstance(Coalesce, type)`
- A004 `assert` L15: `issubclass(PathAccessError, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `glom`
- source entrypoints: `glom.glom, glom.T, glom.Coalesce`
- oracle source files: `repo/glom/core.py, repo/glom/__init__.py`
- runtime dependencies: `none`
- oracle notes: Bounded glom interpreter subset.
