# dataclasses_json__serde_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `FAIL`
- tests/assertions: `13/31`

## Required API

- `featurelifted.DataClassJsonMixin` (class) `()`
- `featurelifted.LetterCase` (class) `(new_class_name, /, names, *, module=None, qualname=None, type=None, start=1, boundary=None)`
- `featurelifted.Exclude` (class) `()`
- `featurelifted.Undefined` (class) `(*values)`
- `featurelifted.Undefined.RAISE` (attribute)
- `featurelifted.dataclass_json` (function) `(_cls: Optional[Type[~T]] = None, *, letter_case: Optional[LetterCase] = None, undefined: Union[str, Undefined, NoneType] = None) -> Union[Callable[[Type[~T]], Type[~T]], Type[~T]]`
- `featurelifted.config` (function) `(metadata: Optional[dict] = None, *, encoder: Optional[Callable] = None, decoder: Optional[Callable] = None, mm_field: Optional[Any] = None, letter_case: Union[Callable[[str], str], LetterCase, NoneType] = None, undefined: Union[str, Undefined, NoneType] = None, field_name: Optional[str] = None, exclude: Optional[Callable[[~T], bool]] = None) -> Dict[str, dict]`
- `featurelifted.global_config` (object)
- `featurelifted.undefined` (module)
- `featurelifted.undefined.UndefinedParameterError` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: round-trip dataclass instances through JSON and dict payloads. Required observable cases include basic json roundtrip; dict roundtrip; undefined raise on extra keys.
- **B002**: The extracted feature must support this observable behavior: apply class-level and field-level letter case transforms. Required observable cases include class level camel case; field level camel case; duplicate letter case encoding error.
- **B003**: The extracted feature must support this observable behavior: exclude fields via config predicates and Exclude helpers. Required observable cases include field name override; exclude always; exclude custom predicate.
- **B004**: The extracted feature must support this observable behavior: register per-type encoders and decoders via config and global_config. Required observable cases include global config encoder decoder.
- **B005**: The extracted feature must support this observable behavior: decode nested dataclass fields recursively. Required observable cases include field name override; nested dataclass roundtrip.
- **B006**: The extracted feature must support this observable behavior: reject unknown keys when undefined=Undefined.RAISE. Required observable cases include undefined raise on extra keys.
- **B007**: The package exposes the required task API paths `featurelifted.DataClassJsonMixin`, `featurelifted.LetterCase`, `featurelifted.Exclude`, `featurelifted.Undefined`, `featurelifted.Undefined.RAISE`, `featurelifted.dataclass_json`, `featurelifted.config`, `featurelifted.global_config`, `featurelifted.undefined`, `featurelifted.undefined.UndefinedParameterError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_basic_json_roundtrip`

- mapping: `B001`
- API: `none detected`
- risk: `none`
- A001 `assert` L23: `inst.to_json() == '{"name": "Ada", "age": 36}'`
- A002 `assert` L24: `Person.from_json('{"name": "Ada", "age": 36}') == inst`

### `public_tests/test_public_api.py::test_dict_roundtrip`

- mapping: `B001`
- API: `none detected`
- risk: `none`
- A001 `assert` L30: `payload == {'name': 'Grace', 'age': 85}`
- A002 `assert` L31: `Person.from_dict(payload) == inst`

### `public_tests/test_public_api.py::test_class_level_camel_case`

- mapping: `B002`
- API: `none detected`
- risk: `none`
- A001 `assert` L36: `inst.to_json() == '{"givenName": "Alice"}'`
- A002 `assert` L37: `CamelPerson.from_json('{"givenName": "Alice"}') == inst`

### `public_tests/test_public_api.py::test_field_name_override`

- mapping: `B003, B005`
- API: `featurelifted.config, featurelifted.dataclass_json`
- risk: `none`
- A001 `assert` L47: `inst.to_dict() == {'givenName': 'Bob'}`
- A002 `assert` L48: `AliasPerson.from_dict({'givenName': 'Bob'}) == inst`

### `hidden_tests/test_hidden_behavior.py::test_field_level_camel_case`

- mapping: `B002`
- API: `featurelifted.undefined`
- risk: `none`
- A001 `assert` L88: `inst.to_json() == '{"givenName": "Alice"}'`
- A002 `assert` L89: `CamelFieldPerson.from_json('{"givenName": "Alice"}') == inst`

### `hidden_tests/test_hidden_behavior.py::test_exclude_always`

- mapping: `B003`
- API: `featurelifted.undefined`
- risk: `none`
- A001 `assert` L95: `encoded == {'public_field': 'public'}`

### `hidden_tests/test_hidden_behavior.py::test_exclude_custom_predicate`

- mapping: `B003`
- API: `featurelifted.undefined`
- risk: `none`
- A001 `assert` L101: `'sensitive_field' in visible.to_dict()`
- A002 `assert` L102: `'sensitive_field' not in hidden.to_dict()`

### `hidden_tests/test_hidden_behavior.py::test_nested_dataclass_roundtrip`

- mapping: `B005`
- API: `featurelifted.undefined`
- risk: `none`
- A001 `assert` L108: `inst.to_dict() == payload`
- A002 `assert` L109: `Outer.from_dict(payload) == inst`
- A003 `assert` L110: `inst.to_json() == '{"inner": {"value": 7}, "label": "edge"}'`

### `hidden_tests/test_hidden_behavior.py::test_undefined_raise_on_extra_keys`

- mapping: `B001, B006`
- API: `featurelifted.undefined`
- risk: `exception_semantics`
- A001 `raises` L114: `pytest.raises(UndefinedParameterError)`

### `hidden_tests/test_hidden_behavior.py::test_duplicate_letter_case_encoding_error`

- mapping: `B002`
- API: `featurelifted.undefined`
- risk: `exact_error_text, exception_semantics`
- A001 `raises` L121: `pytest.raises(ValueError, match='Multiple fields map to the same JSON key')`

### `hidden_tests/test_hidden_behavior.py::test_global_config_encoder_decoder`

- mapping: `B004`
- API: `featurelifted.global_config, featurelifted.global_config.decoders, featurelifted.global_config.encoders, featurelifted.undefined`
- risk: `time_or_randomness`
- A001 `assert` L132: `payload == {'created_at': '2020-01-02T03:04:05'}`
- A002 `assert` L133: `Timestamped.from_dict(payload).created_at == stamp`

### `hidden_tests/test_hidden_behavior.py::test_no_dataclasses_json_import_surface`

- mapping: `B008`
- API: `featurelifted.__file__, featurelifted.undefined`
- risk: `filesystem_resource`
- A001 `assert` L149: `not import_pattern.search(text)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B007`
- API: `featurelifted.DataClassJsonMixin, featurelifted.Exclude, featurelifted.LetterCase, featurelifted.Undefined, featurelifted.config, featurelifted.dataclass_json, featurelifted.global_config, featurelifted.undefined`
- risk: `none`
- A001 `assert` L16: `isinstance(DataClassJsonMixin, type)`
- A002 `assert` L17: `isinstance(LetterCase, type)`
- A003 `assert` L18: `isinstance(Exclude, type)`
- A004 `assert` L19: `isinstance(Undefined, type)`
- A005 `assert` L20: `Undefined is not None`
- A006 `assert` L21: `callable(dataclass_json)`
- A007 `assert` L22: `callable(config)`
- A008 `assert` L23: `global_config is not None`
- A009 `assert` L24: `undefined is not None`
- A010 `assert` L25: `issubclass(getattr(undefined, 'UndefinedParameterError'), BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `typing-inspect`
- forbidden imports: `dataclasses_json, dataclasses-json, marshmallow`
- source entrypoints: `dataclasses_json.dataclass_json, dataclasses_json.DataClassJsonMixin, dataclasses_json.config, dataclasses_json.LetterCase, dataclasses_json.Exclude, dataclasses_json.global_config, dataclasses_json.core._asdict, dataclasses_json.core._decode_dataclass, dataclasses_json.undefined.Undefined`
- oracle source files: `dataclasses_json/__init__.py, dataclasses_json/__version__.py, dataclasses_json/api.py, dataclasses_json/core.py, dataclasses_json/cfg.py, dataclasses_json/utils.py, dataclasses_json/stringcase.py, dataclasses_json/undefined.py`
- runtime dependencies: `none`
- oracle notes: Oracle copies serde core without mm.py marshmallow schema generation. Copy-all baseline includes the full dataclasses_json package and upstream tests tree.

## Machine Issues

- public_tests/test_public_api.py uses undeclared API reference featurelifted.LetterCase.CAMEL
- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.Exclude.ALWAYS
- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.LetterCase.CAMEL
- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.global_config.decoders
- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.global_config.encoders
