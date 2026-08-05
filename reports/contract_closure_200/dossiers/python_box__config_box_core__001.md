# python_box__config_box_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `10/22`

## Required API

- `featurelifted.Box` (class) `(*args: 'Any', default_box: 'bool' = False, default_box_attr: 'Any' = <object object>, default_box_none_transform: 'bool' = True, default_box_create_on_get: 'bool' = True, frozen_box: 'bool' = False, camel_killer_box: 'bool' = False, conversion_box: 'bool' = True, modify_tuples_box: 'bool' = False, box_safe_prefix: 'str' = 'x', box_duplicates: 'str' = 'ignore', box_intact_types: 'tuple | list' = (), box_recast: 'dict | None' = None, box_dots: 'bool' = False, box_dots_exclude: 'str | None' = None, box_class: 'dict | type[Box] | None' = None, box_namespace: 'tuple[str, ...] | Literal[False]' = (), **kwargs: 'Any')`
- `featurelifted.ConfigBox` (class) `(*args: 'Any', default_box: 'bool' = False, default_box_attr: 'Any' = <object object>, default_box_none_transform: 'bool' = True, default_box_create_on_get: 'bool' = True, frozen_box: 'bool' = False, camel_killer_box: 'bool' = False, conversion_box: 'bool' = True, modify_tuples_box: 'bool' = False, box_safe_prefix: 'str' = 'x', box_duplicates: 'str' = 'ignore', box_intact_types: 'tuple | list' = (), box_recast: 'dict | None' = None, box_dots: 'bool' = False, box_dots_exclude: 'str | None' = None, box_class: 'dict | type[Box] | None' = None, box_namespace: 'tuple[str, ...] | Literal[False]' = (), **kwargs: 'Any')`
- `featurelifted.ConfigBox.bool` (method) `(self, item, default=None)`
- `featurelifted.ConfigBox.float` (method) `(self, item, default=None)`
- `featurelifted.ConfigBox.getboolean` (method) `(self, item, default=None)`
- `featurelifted.ConfigBox.getfloat` (method) `(self, item, default=None)`
- `featurelifted.ConfigBox.int` (method) `(self, item, default=None)`
- `featurelifted.ConfigBox.list` (method) `(self, item, default=None, spliter: 'str' = ',', strip=True, mod=None)`
- `featurelifted.exceptions` (module)
- `featurelifted.exceptions.BoxKeyError` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: dot and bracket dict access. Required observable cases include dot access; no box import surface.
- **B002**: The extracted feature must support this observable behavior: case-insensitive ConfigBox keys. Required observable cases include case insensitive key lookup; getboolean alias; missing key raises.
- **B003**: The extracted feature must support this observable behavior: bool/int/float/list coercion helpers. Required observable cases include bool yes no; int coercion; list with mod callback; float and getfloat default.
- **B004**: The extracted feature must support this observable behavior: default values on missing keys. Required observable cases include float and getfloat default; missing key raises.
- **B005**: The package exposes the required task API paths `featurelifted.Box`, `featurelifted.ConfigBox`, `featurelifted.ConfigBox.bool`, `featurelifted.ConfigBox.float`, `featurelifted.ConfigBox.getboolean`, `featurelifted.ConfigBox.getfloat`, `featurelifted.ConfigBox.int`, `featurelifted.ConfigBox.list`, `featurelifted.exceptions`, `featurelifted.exceptions.BoxKeyError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_dot_access`

- mapping: `B001`
- API: `featurelifted.ConfigBox`
- risk: `none`
- A001 `assert` L8: `cfg.host == 'localhost'`
- A002 `assert` L9: `cfg.port == '8080'`

### `public_tests/test_public_api.py::test_bool_yes_no`

- mapping: `B003`
- API: `featurelifted.ConfigBox`
- risk: `none`
- A001 `assert` L14: `cfg.bool('enabled') is True`
- A002 `assert` L15: `cfg.bool('disabled') is False`

### `public_tests/test_public_api.py::test_int_coercion`

- mapping: `B003`
- API: `featurelifted.ConfigBox`
- risk: `none`
- A001 `assert` L20: `cfg.int('retries') == 3`

### `hidden_tests/test_hidden_behavior.py::test_case_insensitive_key_lookup`

- mapping: `B002`
- API: `featurelifted.ConfigBox, featurelifted.exceptions`
- risk: `none`
- A001 `assert` L14: `cfg.bool('MY_FLAG') is True`

### `hidden_tests/test_hidden_behavior.py::test_list_with_mod_callback`

- mapping: `B003`
- API: `featurelifted.ConfigBox, featurelifted.exceptions`
- risk: `none`
- A001 `assert` L19: `cfg.list('items', mod=lambda x: int(x.strip())) == [1, 2, 3]`

### `hidden_tests/test_hidden_behavior.py::test_float_and_getfloat_default`

- mapping: `B003, B004`
- API: `featurelifted.ConfigBox, featurelifted.exceptions`
- risk: `none`
- A001 `assert` L24: `cfg.float('rate') == 2.5`
- A002 `assert` L25: `cfg.getfloat('missing', 1.5) == 1.5`

### `hidden_tests/test_hidden_behavior.py::test_getboolean_alias`

- mapping: `B002`
- API: `featurelifted.ConfigBox, featurelifted.exceptions`
- risk: `none`
- A001 `assert` L30: `cfg.getboolean('flag') is False`

### `hidden_tests/test_hidden_behavior.py::test_missing_key_raises`

- mapping: `B002, B004`
- API: `featurelifted.ConfigBox, featurelifted.exceptions`
- risk: `exception_semantics`
- A001 `raises` L35: `pytest.raises(BoxKeyError)`

### `hidden_tests/test_hidden_behavior.py::test_no_box_import_surface`

- mapping: `B001, B006`
- API: `featurelifted.__file__, featurelifted.exceptions`
- risk: `filesystem_resource`
- A001 `assert` L45: `not import_pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.Box, featurelifted.ConfigBox, featurelifted.exceptions`
- risk: `none`
- A001 `assert` L11: `isinstance(Box, type)`
- A002 `assert` L12: `isinstance(ConfigBox, type)`
- A003 `assert` L13: `hasattr(ConfigBox, 'bool')`
- A004 `assert` L14: `hasattr(ConfigBox, 'float')`
- A005 `assert` L15: `hasattr(ConfigBox, 'getboolean')`
- A006 `assert` L16: `hasattr(ConfigBox, 'getfloat')`
- A007 `assert` L17: `hasattr(ConfigBox, 'int')`
- A008 `assert` L18: `hasattr(ConfigBox, 'list')`
- A009 `assert` L19: `exceptions is not None`
- A010 `assert` L20: `issubclass(getattr(exceptions, 'BoxKeyError'), BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `box`
- source entrypoints: `box.config_box.ConfigBox, box.box.Box`
- oracle source files: `box/box.py, box/config_box.py, box/exceptions.py`
- runtime dependencies: `none`
- oracle notes: Oracle is Box+ConfigBox core with stub converters; repo includes converters/from_file/shorthand for copy-all penalty.
