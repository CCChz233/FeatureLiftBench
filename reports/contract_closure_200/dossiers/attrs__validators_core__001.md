# attrs__validators_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `FAIL`
- tests/assertions: `7/12`

## Required API

- `featurelifted.define` (function) `(maybe_cls=None, *, these=None, repr=None, unsafe_hash=None, hash=None, init=None, slots=True, frozen=False, weakref_slot=True, str=False, auto_attribs=None, kw_only=False, cache_hash=False, auto_exc=True, eq=None, order=False, auto_detect=True, getstate_setstate=None, on_setattr=None, field_transformer=None, match_args=True)`
- `featurelifted.field` (function) `(*, default=NOTHING, validator=None, repr=True, hash=None, init=True, metadata=None, type=None, converter=None, factory=None, kw_only=False, eq=None, order=None, on_setattr=None, alias=None)`
- `featurelifted.validate` (function) `(inst)`
- `featurelifted.validators` (module)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: attach validators to fields on define() classes. Required observable cases include set disabled skips validation.
- **B002**: The extracted feature must support this observable behavior: run instance_of, ge, lt, matches_re, in_, and length validators. Required observable cases include valid instance passes; instance of rejects wrong type; matches re and deep iterable.
- **B003**: The extracted feature must support this observable behavior: compose validators with and_, not_, and optional. Required observable cases include set disabled skips validation.
- **B004**: The extracted feature must support this observable behavior: validate deep_iterable and deep_mapping structures. Required observable cases include matches re and deep iterable; deep mapping validates keys and values; optional allows none and validates present values.
- **B005**: The extracted feature must support this observable behavior: globally disable validators with set_disabled and validate(). Required observable cases include optional allows none and validates present values; set disabled skips validation.
- **B006**: The package exposes the required task API paths `featurelifted.define`, `featurelifted.field`, `featurelifted.validate`, `featurelifted.validators` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_validators_public.py::test_valid_instance_passes`

- mapping: `B002`
- API: `featurelifted.validate`
- risk: `none`
- A001 `assert` L18: `user.name == 'Ada'`

### `public_tests/test_validators_public.py::test_instance_of_rejects_wrong_type`

- mapping: `B002`
- API: `none detected`
- risk: `exception_semantics`
- A001 `raises` L22: `pytest.raises(TypeError)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.define, featurelifted.field, featurelifted.validate, featurelifted.validators`
- risk: `none`
- A001 `assert` L12: `callable(define)`
- A002 `assert` L13: `callable(field)`
- A003 `assert` L14: `callable(validate)`
- A004 `assert` L15: `validators is not None`

### `hidden_tests/test_validators_hidden.py::test_matches_re_and_deep_iterable`

- mapping: `B002, B004`
- API: `featurelifted.validate`
- risk: `exception_semantics`
- A001 `raises` L19: `pytest.raises(ValueError)`
- A002 `raises` L22: `pytest.raises(TypeError)`

### `hidden_tests/test_validators_hidden.py::test_deep_mapping_validates_keys_and_values`

- mapping: `B004`
- API: `none detected`
- risk: `exception_semantics`
- A001 `raises` L39: `pytest.raises(TypeError)`
- A002 `raises` L42: `pytest.raises(TypeError)`

### `hidden_tests/test_validators_hidden.py::test_optional_allows_none_and_validates_present_values`

- mapping: `B004, B005`
- API: `none detected`
- risk: `exception_semantics`
- A001 `raises` L55: `pytest.raises(TypeError)`

### `hidden_tests/test_validators_hidden.py::test_set_disabled_skips_validation`

- mapping: `B001, B003, B005`
- API: `featurelifted.define, featurelifted.field, featurelifted.validate, featurelifted.validators, featurelifted.validators.instance_of, featurelifted.validators.set_disabled`
- risk: `exception_semantics`
- A001 `raises` L71: `pytest.raises(TypeError)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `attrs, attr`
- source entrypoints: `attrs.define, attrs.field, attrs.validators, attrs.validate, attr._make._AndValidator`
- oracle source files: `none`
- runtime dependencies: `none`

## Machine Issues

- public_tests/test_validators_public.py uses undeclared API reference featurelifted.validators.and_
- public_tests/test_validators_public.py uses undeclared API reference featurelifted.validators.ge
- public_tests/test_validators_public.py uses undeclared API reference featurelifted.validators.instance_of
- hidden_tests/test_validators_hidden.py uses undeclared API reference featurelifted.validators.deep_iterable
- hidden_tests/test_validators_hidden.py uses undeclared API reference featurelifted.validators.deep_mapping
- hidden_tests/test_validators_hidden.py uses undeclared API reference featurelifted.validators.instance_of
- hidden_tests/test_validators_hidden.py uses undeclared API reference featurelifted.validators.matches_re
- hidden_tests/test_validators_hidden.py uses undeclared API reference featurelifted.validators.min_len
- hidden_tests/test_validators_hidden.py uses undeclared API reference featurelifted.validators.optional
- hidden_tests/test_validators_hidden.py uses undeclared API reference featurelifted.validators.set_disabled
