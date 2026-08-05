# tox__factor_expression_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `3/8`

## Required API

- `featurelifted.expand_factors` (function) `(value: 'str') -> 'Iterator[tuple[list[list[tuple[str, bool]]] | None, str]]'`
- `featurelifted.find_envs` (function) `(value: 'str') -> 'list[str]'`
- `featurelifted.filter_for_env` (function) `(value: 'str', env_name: 'str | None', env_factors: 'set[str] | None' = None) -> 'str'`

## Public Behaviors

- **B001**: `find_envs` discovers environment names from brace factor expressions.
- **B002**: When factor expressions contain negation, filter_for_env accepts an environment only when positive factors match and negated factors do not.
- **B003**: find_envs expands brace and factor expressions into the deterministic set of environment names they describe.
- **B004**: `filter_for_env` keeps lines whose factor expressions match `env_name` and/or `env_factors`.
- **B005**: The package exposes the required task API paths `featurelifted.expand_factors`, `featurelifted.find_envs`, `featurelifted.filter_for_env` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_find_envs_brace_groups`

- mapping: `B001, B003`
- API: `featurelifted.find_envs`
- risk: `none`
- A001 `assert` L6: `set(find_envs('{lint,test}-py')) == {'lint-py', 'test-py'}`

### `hidden_tests/test_hidden_contract.py::test_filter_for_env_by_factors`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.filter_for_env`
- risk: `none`
- A001 `assert` L8: `'included' in result`
- A002 `assert` L9: `'also' in result`
- A003 `assert` L10: `'excluded' not in result`
- A004 `assert` L11: `'skip' not in result`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.expand_factors, featurelifted.filter_for_env, featurelifted.find_envs`
- risk: `none`
- A001 `assert` L11: `callable(expand_factors)`
- A002 `assert` L12: `callable(find_envs)`
- A003 `assert` L13: `callable(filter_for_env)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `tox`
- source entrypoints: `tox.config.loader.ini.factor.filter_for_env`
- oracle source files: `repo/src/tox/config/loader/ini/factor.py`
- runtime dependencies: `none`
- oracle notes: Factor expression and ini filtering subset without environment execution.
