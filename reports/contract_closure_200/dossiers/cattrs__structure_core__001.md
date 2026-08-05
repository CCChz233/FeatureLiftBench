# cattrs__structure_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `10/32`

## Required API

- `featurelifted.Converter` (class) `(dict_factory: Callable[[], Any] = <class 'dict'>, unstruct_strat: UnstructureStrategy = <UnstructureStrategy.AS_DICT: 'asdict'>, omit_if_default: bool = False, forbid_extra_keys: bool = False, type_overrides: collections.abc.Mapping[typing.Type, AttributeOverride] = {}, unstruct_collection_overrides: collections.abc.Mapping[typing.Type, typing.Callable] = {}, prefer_attrib_converters: bool = False, detailed_validation: bool = True, unstructure_fallback_factory: Callable[[Any], Callable[[Any], Any]] = <function Converter.<lambda>>, structure_fallback_factory: Callable[[Any], Callable[[Any, Any], Any]] = <function Converter.<lambda>>)`
- `featurelifted.Converter.structure` (method) `(self, obj: Any, cl: Type[~T]) -> ~T`
- `featurelifted.Converter.register_structure_hook` (method) `(self, cl: Any, func: Callable[[Any, Any], Any]) -> None`
- `featurelifted.Converter.register_unstructure_hook` (method) `(self, cls: Any, func: Callable[[Any], Any]) -> None`
- `featurelifted.Converter.unstructure` (method) `(self, obj: Any, unstructure_as: Any = None) -> Any`
- `featurelifted.structure` (function) `(obj: Any, cl: Type[~T]) -> ~T`
- `featurelifted.unstructure` (function) `(obj: Any, unstructure_as: Any = None) -> Any`
- `featurelifted.errors` (module)
- `featurelifted.errors.ClassValidationError` (exception)
- `featurelifted.errors.ForbiddenExtraKeysError` (exception)
- `featurelifted.gen` (module)
- `featurelifted.gen.make_dict_structure_fn` (function) `(cl: 'type[T]', converter: 'BaseConverter', _cattrs_forbid_extra_keys: "bool | Literal['from_converter']" = 'from_converter', _cattrs_use_linecache: 'bool' = True, _cattrs_prefer_attrib_converters: 'bool' = False, _cattrs_detailed_validation: "bool | Literal['from_converter']" = 'from_converter', _cattrs_use_alias: 'bool' = False, _cattrs_include_init_false: 'bool' = False, **kwargs: 'AttributeOverride') -> 'DictStructureFn[T]'`
- `featurelifted.gen.make_dict_unstructure_fn` (function) `(cl: 'type[T]', converter: 'BaseConverter', _cattrs_omit_if_default: 'bool' = False, _cattrs_use_linecache: 'bool' = True, _cattrs_use_alias: 'bool' = False, _cattrs_include_init_false: 'bool' = False, **kwargs: 'AttributeOverride') -> 'Callable[[T], dict[str, Any]]'`
- `featurelifted.gen.override` (function) `(omit_if_default: 'bool | None' = None, rename: 'str | None' = None, omit: 'bool | None' = None, struct_hook: 'Callable[[Any, Any], Any] | None' = None, unstruct_hook: 'Callable[[Any], Any] | None' = None) -> 'AttributeOverride'`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: round-trip attrs and dataclass instances through dict payloads. Required observable cases include nested attrs and dataclass.
- **B002**: The extracted feature must support this observable behavior: structure and unstructure nested mappings and sequences. Required observable cases include attrs roundtrip; dataclass roundtrip; nested attrs and dataclass; optional none field.
- **B003**: The extracted feature must support this observable behavior: register custom dict structure/unstructure hooks via gen helpers. Required observable cases include attrs roundtrip; dataclass roundtrip; module level helpers; structure hook rename override; optional none field.
- **B004**: The extracted feature must support this observable behavior: apply per-field rename and omit_if_default overrides. Required observable cases include structure hook rename override; unstructure omit if default.
- **B005**: The extracted feature must support this observable behavior: reject extra dict keys when forbid_extra_keys is enabled. Required observable cases include forbid extra keys.
- **B006**: The package exposes the required task API paths `featurelifted.Converter`, `featurelifted.Converter.structure`, `featurelifted.Converter.register_structure_hook`, `featurelifted.Converter.register_unstructure_hook`, `featurelifted.Converter.unstructure`, `featurelifted.structure`, `featurelifted.unstructure`, `featurelifted.errors`, `featurelifted.errors.ClassValidationError`, `featurelifted.errors.ForbiddenExtraKeysError`, `featurelifted.gen`, `featurelifted.gen.make_dict_structure_fn`, and 2 listed members with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_attrs_roundtrip`

- mapping: `B002, B003`
- API: `featurelifted.Converter`
- risk: `none`
- A001 `assert` L25: `payload == {'x': 1, 'y': 2}`
- A002 `assert` L26: `converter.structure(payload, Point) == inst`

### `public_tests/test_public_api.py::test_dataclass_roundtrip`

- mapping: `B002, B003`
- API: `featurelifted.Converter`
- risk: `none`
- A001 `assert` L33: `payload == {'text': 'north'}`
- A002 `assert` L34: `converter.structure(payload, Label) == inst`

### `public_tests/test_public_api.py::test_module_level_helpers`

- mapping: `B003`
- API: `featurelifted.structure, featurelifted.unstructure`
- risk: `none`
- A001 `assert` L40: `payload == {'x': 3, 'y': 4}`
- A002 `assert` L41: `structure(payload, Point) == inst`

### `hidden_tests/test_hidden_behavior.py::test_nested_attrs_and_dataclass`

- mapping: `B001, B002`
- API: `featurelifted.Converter, featurelifted.errors, featurelifted.gen`
- risk: `none`
- A001 `assert` L41: `converter.unstructure(inst) == payload`
- A002 `assert` L42: `converter.structure(payload, Container) == inst`

### `hidden_tests/test_hidden_behavior.py::test_structure_hook_rename_override`

- mapping: `B003, B004`
- API: `featurelifted.Converter, featurelifted.errors, featurelifted.gen`
- risk: `none`
- A001 `assert` L50: `obj.label == 'edge'`
- A002 `assert` L51: `obj.inner.value == 7`

### `hidden_tests/test_hidden_behavior.py::test_unstructure_omit_if_default`

- mapping: `B004`
- API: `featurelifted.Converter, featurelifted.errors, featurelifted.gen`
- risk: `none`
- A001 `assert` L60: `'label' not in payload`
- A002 `assert` L61: `payload == {'inner': {'value': 2}}`

### `hidden_tests/test_hidden_behavior.py::test_forbid_extra_keys`

- mapping: `B005`
- API: `featurelifted.Converter, featurelifted.errors, featurelifted.gen`
- risk: `exception_semantics`
- A001 `raises` L71: `pytest.raises(ClassValidationError)`
- A002 `assert` L73: `len(excinfo.value.exceptions) == 1`
- A003 `assert` L74: `isinstance(excinfo.value.exceptions[0], ForbiddenExtraKeysError)`

### `hidden_tests/test_hidden_behavior.py::test_optional_none_field`

- mapping: `B002, B003`
- API: `featurelifted.Converter, featurelifted.errors, featurelifted.gen`
- risk: `none`
- A001 `assert` L85: `payload == {'note': None}`
- A002 `assert` L86: `converter.structure({'note': None}, Maybe) == inst`

### `hidden_tests/test_hidden_behavior.py::test_no_cattrs_import_surface`

- mapping: `B007`
- API: `featurelifted.__file__, featurelifted.errors, featurelifted.gen`
- risk: `filesystem_resource`
- A001 `assert` L96: `not import_pattern.search(text)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.Converter, featurelifted.errors, featurelifted.gen, featurelifted.structure, featurelifted.unstructure`
- risk: `none`
- A001 `assert` L13: `isinstance(Converter, type)`
- A002 `assert` L14: `hasattr(Converter, 'structure')`
- A003 `assert` L15: `hasattr(Converter, 'register_structure_hook')`
- A004 `assert` L16: `hasattr(Converter, 'register_unstructure_hook')`
- A005 `assert` L17: `hasattr(Converter, 'unstructure')`
- A006 `assert` L18: `callable(structure)`
- A007 `assert` L19: `callable(unstructure)`
- A008 `assert` L20: `errors is not None`
- A009 `assert` L21: `issubclass(getattr(errors, 'ClassValidationError'), BaseException)`
- A010 `assert` L22: `issubclass(getattr(errors, 'ForbiddenExtraKeysError'), BaseException)`
- A011 `assert` L23: `gen is not None`
- A012 `assert` L24: `callable(getattr(gen, 'make_dict_structure_fn'))`
- A013 `assert` L25: `callable(getattr(gen, 'make_dict_unstructure_fn'))`
- A014 `assert` L26: `callable(getattr(gen, 'override'))`

## Dependency / Oracle Evidence

- allowed dependencies: `attrs`
- forbidden imports: `cattrs`
- source entrypoints: `cattrs.Converter, cattrs.Converter.structure, cattrs.Converter.unstructure, cattrs.structure, cattrs.unstructure, cattrs.gen.make_dict_structure_fn, cattrs.gen.make_dict_unstructure_fn, cattrs.gen.override, cattrs.dispatch.MultiStrategyDispatch, cattrs.errors.ClassValidationError`
- oracle source files: `cattrs/_compat.py, cattrs/_generics.py, cattrs/converters.py, cattrs/disambiguators.py, cattrs/dispatch.py, cattrs/errors.py, cattrs/fns.py, cattrs/gen/__init__.py, cattrs/gen/_consts.py, cattrs/gen/_shared.py, cattrs/gen/_generics.py, cattrs/gen/_lc.py, cattrs/gen/typeddicts.py`
- runtime dependencies: `none`
- oracle notes: Oracle copies the structure/unstructure core without preconf codecs, strategies registries, or GenConverter. Copy-all baseline includes the full cattrs package tree under repo/cattrs/.
