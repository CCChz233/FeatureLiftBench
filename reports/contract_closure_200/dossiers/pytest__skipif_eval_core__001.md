# pytest__skipif_eval_core__001

- release: `frozen_python150`
- lift: `Composite`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `6/9`

## Required API

- `featurelifted.Mark` (class) `(name: 'str', kwargs: 'Mapping[str, Any]' = <factory>) -> None`
- `featurelifted.EvalContext` (class) `(config: 'Any' = None, obj_globals: 'Mapping[str, Any] | None' = None, markeval_namespace: 'Sequence[Mapping[str, Any]]' = ()) -> None`
- `featurelifted.evaluate_condition` (function) `(context: 'EvalContext', mark: 'Mark', condition: 'object') -> 'tuple[bool, str]'`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: evaluate string conditions via compile/eval with allowed globals. Required observable cases include string condition true; obj globals merged; invalid syntax raises.
- **B002**: The extracted feature must support this observable behavior: evaluate boolean conditions directly. Required observable cases include boolean condition; obj globals merged.
- **B003**: The extracted feature must support this observable behavior: merge markeval_namespace mappings into eval globals. Required observable cases include markeval namespace merged; obj globals merged.
- **B004**: The extracted feature must support this observable behavior: return (result, reason) tuple with default reason for string conditions. Required observable cases include string condition true; obj globals merged.
- **B005**: The package exposes the required task API paths `featurelifted.Mark`, `featurelifted.EvalContext`, `featurelifted.evaluate_condition` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_string_condition_true`

- mapping: `B001, B004`
- API: `featurelifted.EvalContext, featurelifted.Mark, featurelifted.evaluate_condition`
- risk: `none`
- A001 `assert` L12: `result == (sys.platform == 'win32')`
- A002 `assert` L13: `reason == 'win32'`

### `public_tests/test_public_api.py::test_boolean_condition`

- mapping: `B002`
- API: `featurelifted.EvalContext, featurelifted.Mark, featurelifted.evaluate_condition`
- risk: `none`
- A001 `assert` L19: `evaluate_condition(ctx, mark, True) == (True, 'disabled')`

### `hidden_tests/test_hidden_behavior.py::test_markeval_namespace_merged`

- mapping: `B003`
- API: `featurelifted.EvalContext, featurelifted.Mark, featurelifted.evaluate_condition`
- risk: `none`
- A001 `assert` L12: `result is True`

### `hidden_tests/test_hidden_behavior.py::test_obj_globals_merged`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.EvalContext, featurelifted.Mark, featurelifted.evaluate_condition`
- risk: `none`
- A001 `assert` L19: `result is True`

### `hidden_tests/test_hidden_behavior.py::test_invalid_syntax_raises`

- mapping: `B001`
- API: `featurelifted.EvalContext, featurelifted.Mark, featurelifted.evaluate_condition`
- risk: `exception_semantics`
- A001 `raises` L27: `pytest.raises(Exception)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.EvalContext, featurelifted.Mark, featurelifted.evaluate_condition`
- risk: `none`
- A001 `assert` L11: `isinstance(Mark, type)`
- A002 `assert` L12: `isinstance(EvalContext, type)`
- A003 `assert` L13: `callable(evaluate_condition)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `pytest, _pytest`
- source entrypoints: `_pytest.skipping.evaluate_condition`
- oracle source files: `none`
- runtime dependencies: `none`
- oracle notes: evaluate_condition subset extracted from skipping.py with local Mark/EvalContext types.
