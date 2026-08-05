# environs__typed_env_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `FAIL`
- tests/assertions: `14/27`

## Required API

- `featurelifted.Env` (class) `(*, eager: '_BoolType' = True, expand_vars: '_BoolType' = False, prefix: '_StrType | None' = None)`
- `featurelifted.Env.int` (method) `(self: 'Env', name: 'str', default: 'typing.Any' = Ellipsis, subcast: 'Subcast[_T] | None' = None, *, validate: 'typing.Callable[[typing.Any], typing.Any] | typing.Iterable[typing.Callable[[typing.Any], typing.Any]] | None' = None, **kwargs) -> '_T | None'`
- `featurelifted.Env.prefixed` (method) `(self, prefix: '_StrType') -> 'typing.Iterator[Env]'`
- `featurelifted.Env.seal` (method) `(self) -> 'None'`
- `featurelifted.Env.str` (method) `(self: 'Env', name: 'str', default: 'typing.Any' = Ellipsis, subcast: 'Subcast[_T] | None' = None, *, validate: 'typing.Callable[[typing.Any], typing.Any] | typing.Iterable[typing.Callable[[typing.Any], typing.Any]] | None' = None, **kwargs) -> '_T | None'`
- `featurelifted.EnvError` (exception)
- `featurelifted.EnvValidationError` (exception)
- `featurelifted.EnvSealedError` (exception)
- `featurelifted.ParserConflictError` (exception)
- `featurelifted.ValidationError` (exception)
- `featurelifted.validate` (module)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: typed casting for int, bool, str with defaults and eager errors. Required observable cases include int cast; bool cast; str default when unset; missing required raises; timedelta gep2257 duration.
- **B002**: The extracted feature must support this observable behavior: marshmallow validate= callables and validators on parsed fields. Required observable cases include marshmallow range validator.
- **B003**: The extracted feature must support this observable behavior: list and dict env strings with delimiter/subcast preprocessing. Required observable cases include list subcast int; dict subcast values.
- **B004**: The extracted feature must support this observable behavior: expand_vars ${VAR:-default} substitution in env values. Required observable cases include expand vars with default; expand vars multiple in string.
- **B005**: The extracted feature must support this observable behavior: constructor and context-manager prefix for env key names. Required observable cases include prefixed context manager.
- **B006**: The extracted feature must support this observable behavior: deferred validation via eager=False and seal() error aggregation. Required observable cases include deferred seal aggregates errors.
- **B007**: The extracted feature must support this observable behavior: custom timedelta duration strings via fields.TimeDelta. Required observable cases include timedelta gep2257 duration.
- **B008**: The package exposes the required task API paths `featurelifted.Env`, `featurelifted.Env.int`, `featurelifted.Env.prefixed`, `featurelifted.Env.seal`, `featurelifted.Env.str`, `featurelifted.EnvError`, `featurelifted.EnvValidationError`, `featurelifted.EnvSealedError`, `featurelifted.ParserConflictError`, `featurelifted.ValidationError`, `featurelifted.validate` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_int_cast`

- mapping: `B001`
- API: `featurelifted.Env`
- risk: `environment_state`
- A001 `assert` L20: `env.int('INT_VAR') == 42`

### `public_tests/test_public_api.py::test_bool_cast`

- mapping: `B001`
- API: `featurelifted.Env`
- risk: `environment_state`
- A001 `assert` L25: `env.bool('BOOL_VAR') is True`
- A002 `assert` L27: `env.bool('BOOL_VAR') is False`

### `public_tests/test_public_api.py::test_str_default_when_unset`

- mapping: `B001`
- API: `featurelifted.Env`
- risk: `exact_error_text`
- A001 `assert` L31: `env.str('STR_VAR', 'fallback') == 'fallback'`

### `public_tests/test_public_api.py::test_missing_required_raises`

- mapping: `B001`
- API: `featurelifted.Env, featurelifted.EnvError`
- risk: `exact_error_text, exception_semantics`
- A001 `raises` L35: `pytest.raises(EnvError, match='Environment variable "INT_VAR" not set')`

### `hidden_tests/test_hidden_behavior.py::test_list_subcast_int`

- mapping: `B003`
- API: `featurelifted.Env`
- risk: `environment_state`
- A001 `assert` L23: `env.list('FLB_LIST', subcast=int) == [1, 2, 3]`

### `hidden_tests/test_hidden_behavior.py::test_dict_subcast_values`

- mapping: `B003`
- API: `featurelifted.Env`
- risk: `environment_state`
- A001 `assert` L28: `env.dict('FLB_DICT', subcast_values=int) == {'a': 1, 'b': 2}`

### `hidden_tests/test_hidden_behavior.py::test_expand_vars_with_default`

- mapping: `B004`
- API: `featurelifted.Env`
- risk: `environment_state, exact_error_text`
- A001 `assert` L34: `expand_env.str('FLB_MAIN_DEF') == 'maindef'`

### `hidden_tests/test_hidden_behavior.py::test_expand_vars_multiple_in_string`

- mapping: `B004`
- API: `featurelifted.Env`
- risk: `environment_state, exact_error_text`
- A001 `assert` L41: `expand_env.str('FLB_PGURL') == 'postgres://gnarvaja:secret@localhost'`

### `hidden_tests/test_hidden_behavior.py::test_marshmallow_range_validator`

- mapping: `B002`
- API: `featurelifted.Env, featurelifted.EnvError, featurelifted.validate, featurelifted.validate.Range`
- risk: `environment_state, exact_error_text, exception_semantics`
- A001 `raises` L46: `pytest.raises(EnvError, match='invalid')`

### `hidden_tests/test_hidden_behavior.py::test_deferred_seal_aggregates_errors`

- mapping: `B006`
- API: `featurelifted.Env, featurelifted.EnvValidationError`
- risk: `environment_state, exception_semantics`
- A001 `raises` L56: `pytest.raises(EnvValidationError)`
- A002 `assert` L59: `'FLB_INT' in messages`
- A003 `assert` L60: `'FLB_REQUIRED' in messages`

### `hidden_tests/test_hidden_behavior.py::test_timedelta_gep2257_duration`

- mapping: `B001, B007`
- API: `featurelifted.Env, featurelifted.Env.timedelta`
- risk: `environment_state`
- A001 `assert` L65: `Env().timedelta('FLB_TD') == dt.timedelta(weeks=42, days=42, hours=42, minutes=42, seconds=42, milliseconds=42, microseconds=42)`

### `hidden_tests/test_hidden_behavior.py::test_prefixed_context_manager`

- mapping: `B005`
- API: `featurelifted.Env`
- risk: `environment_state, exact_error_text`
- A001 `assert` L80: `base.str('STR') == 'hello'`

### `hidden_tests/test_hidden_behavior.py::test_no_environs_import_surface`

- mapping: `B009`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L90: `not import_pattern.search(text)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B008`
- API: `featurelifted.Env, featurelifted.EnvError, featurelifted.EnvSealedError, featurelifted.EnvValidationError, featurelifted.ParserConflictError, featurelifted.ValidationError, featurelifted.validate`
- risk: `none`
- A001 `assert` L15: `isinstance(Env, type)`
- A002 `assert` L16: `hasattr(Env, 'int')`
- A003 `assert` L17: `hasattr(Env, 'prefixed')`
- A004 `assert` L18: `hasattr(Env, 'seal')`
- A005 `assert` L19: `hasattr(Env, 'str')`
- A006 `assert` L20: `issubclass(EnvError, BaseException)`
- A007 `assert` L21: `issubclass(EnvValidationError, BaseException)`
- A008 `assert` L22: `issubclass(EnvSealedError, BaseException)`
- A009 `assert` L23: `issubclass(ParserConflictError, BaseException)`
- A010 `assert` L24: `issubclass(ValidationError, BaseException)`
- A011 `assert` L25: `validate is not None`

## Dependency / Oracle Evidence

- allowed dependencies: `marshmallow`
- forbidden imports: `environs`
- source entrypoints: `environs.Env, environs.Env.int, environs.Env.bool, environs.Env.str, environs.Env.list, environs.Env.dict, environs.Env.timedelta, environs.Env.seal, environs.Env.prefixed, environs.validate, environs.fields.TimeDelta`
- oracle source files: `src/environs/exceptions.py, src/environs/types.py, src/environs/fields.py, src/environs/__init__.py`
- runtime dependencies: `none`
- oracle notes: Oracle copies exceptions, types, fields, and a trimmed env core (__init__ without dotenv, FileAwareEnv, or django URL parsers). Copy-all includes upstream tests for extraction calibration.

## Machine Issues

- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.Env.timedelta
- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.validate.Range
