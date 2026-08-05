# pydantic_v1__validation_error_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `FAIL`
- tests/assertions: `11/28`

## Required API

- `featurelifted.BaseModel` (class) `() -> None`
- `featurelifted.BaseModel.parse_obj` (method) `(obj: Any) -> 'Model'`
- `featurelifted.Field` (function) `(default: Any = PydanticUndefined, *, default_factory: Optional[Callable[[], Any]] = None, alias: Optional[str] = None, title: Optional[str] = None, description: Optional[str] = None, exclude: Union[ForwardRef('AbstractSetIntStr'), ForwardRef('MappingIntStrAny'), Any, NoneType] = None, include: Union[ForwardRef('AbstractSetIntStr'), ForwardRef('MappingIntStrAny'), Any, NoneType] = None, const: Optional[bool] = None, gt: Optional[float] = None, ge: Optional[float] = None, lt: Optional[float] = None, le: Optional[float] = None, multiple_of: Optional[float] = None, allow_inf_nan: Optional[bool] = None, max_digits: Optional[int] = None, decimal_places: Optional[int] = None, min_items: Optional[int] = None, max_items: Optional[int] = None, unique_items: Optional[bool] = None, min_length: Optional[int] = None, max_length: Optional[int] = None, allow_mutation: bool = True, regex: Optional[str] = None, discriminator: Optional[str] = None, repr: bool = True, **extra: Any) -> Any`
- `featurelifted.ValidationError` (exception)
- `featurelifted.validator` (function) `(*fields: str, pre: bool = False, each_item: bool = False, always: bool = False, check_fields: bool = True, whole: Optional[bool] = None, allow_reuse: bool = False) -> Callable[[Callable[..., Any]], ForwardRef('AnyClassMethod')]`
- `featurelifted.root_validator` (function) `(_func: Optional[Callable[..., Any]] = None, *, pre: bool = False, allow_reuse: bool = False, skip_on_failure: bool = False) -> Union[ForwardRef('AnyClassMethod'), Callable[[Callable[..., Any]], ForwardRef('AnyClassMethod')]]`
- `featurelifted.Extra` (class) `(*values)`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: declare BaseModel subclasses and parse dict input. Required observable cases include simple model parses fields; missing required field raises; parse obj classmethod; validator pre runs before type check.
- **B002**: The extracted feature must support this observable behavior: field validators with pre/each_item semantics. Required observable cases include field validator runs; validator pre runs before type check.
- **B003**: The extracted feature must support this observable behavior: root_validator whole-model checks. Required observable cases include root validator rejects invalid combo.
- **B004**: The extracted feature must support this observable behavior: Config.extra forbid for unknown keys. Required observable cases include extra forbid rejects unknown keys.
- **B005**: The extracted feature must support this observable behavior: ValidationError.errors() with loc/type/msg for nested models. Required observable cases include missing required field raises; nested validation error loc paths; multiple errors collected.
- **B006**: The package exposes the required task API paths `featurelifted.BaseModel`, `featurelifted.BaseModel.parse_obj`, `featurelifted.Field`, `featurelifted.ValidationError`, `featurelifted.validator`, `featurelifted.root_validator`, `featurelifted.Extra` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_simple_model_parses_fields`

- mapping: `B001`
- API: `none detected`
- risk: `none`
- A001 `assert` L15: `user.name == 'ada'`
- A002 `assert` L16: `user.age == 30`

### `public_tests/test_public_api.py::test_missing_required_field_raises`

- mapping: `B001, B005`
- API: `featurelifted.ValidationError`
- risk: `exception_semantics`
- A001 `raises` L20: `pytest.raises(ValidationError)`
- A002 `assert` L23: `len(errors) >= 1`
- A003 `assert` L24: `errors[0]['loc'] == ('age',)`
- A004 `assert` L25: `'type' in errors[0]`

### `public_tests/test_public_api.py::test_field_validator_runs`

- mapping: `B002`
- API: `none detected`
- risk: `none`
- A001 `assert` L38: `product.sku == 'AB12'`

### `public_tests/test_public_api.py::test_parse_obj_classmethod`

- mapping: `B001`
- API: `none detected`
- risk: `none`
- A001 `assert` L43: `user.age == 21`

### `hidden_tests/test_hidden_behavior.py::test_nested_validation_error_loc_paths`

- mapping: `B005`
- API: `featurelifted.ValidationError`
- risk: `exception_semantics`
- A001 `raises` L21: `pytest.raises(ValidationError)`
- A002 `assert` L24: `any((err['loc'] == ('items', 0, 'qty') for err in errors))`
- A003 `assert` L25: `any((err['type'] == 'type_error.integer' for err in errors))`

### `hidden_tests/test_hidden_behavior.py::test_extra_forbid_rejects_unknown_keys`

- mapping: `B004`
- API: `featurelifted.ValidationError`
- risk: `exception_semantics`
- A001 `raises` L36: `pytest.raises(ValidationError)`
- A002 `assert` L39: `any((err['type'] == 'value_error.extra' for err in errors))`

### `hidden_tests/test_hidden_behavior.py::test_root_validator_rejects_invalid_combo`

- mapping: `B003`
- API: `featurelifted.ValidationError`
- risk: `exception_semantics`
- A001 `raises` L54: `pytest.raises(ValidationError)`
- A002 `assert` L57: `any((err['loc'] == ('__root__',) for err in errors))`
- A003 `assert` L58: `any((err['type'] == 'value_error' for err in errors))`

### `hidden_tests/test_hidden_behavior.py::test_validator_pre_runs_before_type_check`

- mapping: `B001, B002`
- API: `none detected`
- risk: `none`
- A001 `assert` L73: `model.value == 42`

### `hidden_tests/test_hidden_behavior.py::test_multiple_errors_collected`

- mapping: `B005`
- API: `featurelifted.BaseModel, featurelifted.ValidationError`
- risk: `exception_semantics`
- A001 `raises` L82: `pytest.raises(ValidationError)`
- A002 `assert` L84: `len(exc.value.errors()) >= 2`

### `hidden_tests/test_hidden_behavior.py::test_no_pydantic_import_surface`

- mapping: `B007`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L93: `name not in exports`
- A002 `assert` L98: `not import_pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.BaseModel, featurelifted.Extra, featurelifted.Field, featurelifted.ValidationError, featurelifted.root_validator, featurelifted.validator`
- risk: `none`
- A001 `assert` L14: `isinstance(BaseModel, type)`
- A002 `assert` L15: `hasattr(BaseModel, 'parse_obj')`
- A003 `assert` L16: `callable(Field)`
- A004 `assert` L17: `issubclass(ValidationError, BaseException)`
- A005 `assert` L18: `callable(validator)`
- A006 `assert` L19: `callable(root_validator)`
- A007 `assert` L20: `isinstance(Extra, type)`

## Dependency / Oracle Evidence

- allowed dependencies: `typing_extensions`
- forbidden imports: `pydantic`
- source entrypoints: `pydantic.BaseModel, pydantic.ValidationError, pydantic.validator, pydantic.root_validator, pydantic.Field, pydantic.config.Extra, pydantic.error_wrappers.ValidationError.errors`
- oracle source files: `pydantic/version.py, pydantic/errors.py, pydantic/utils.py, pydantic/typing.py, pydantic/json.py, pydantic/datetime_parse.py, pydantic/config.py, pydantic/error_wrappers.py, pydantic/validators.py, pydantic/types.py, pydantic/class_validators.py, pydantic/fields.py, pydantic/annotated_types.py, pydantic/parse.py, pydantic/main.py`
- runtime dependencies: `none`
- oracle notes: Validation core closure without schema.py, networks.py, env_settings.py, dataclasses.py, mypy.py, tools.py, or generics.py.

## Machine Issues

- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.Extra.forbid
