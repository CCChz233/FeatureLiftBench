# dynaconf__settings_merge_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `7/18`

## Required API

- `featurelifted.Dynaconf` (class) `(wrapped=None, **kwargs)`
- `featurelifted.Dynaconf.BAR` (attribute)
- `featurelifted.Dynaconf.FOO` (attribute)
- `featurelifted.Dynaconf.HOST` (attribute)
- `featurelifted.Dynaconf.LIST` (attribute)
- `featurelifted.Dynaconf.PORT` (attribute)
- `featurelifted.Dynaconf.setenv` (method) `(env=None, clean=True, silent=True, filename=None)`
- `featurelifted.object_merge` (function) `(old: 'Any', new: 'Any', unique: 'bool' = False, full_path: 'Optional[list[str]]' = None, list_merge: 'ListMergeOptions' = 'merge') -> 'Any'`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: recursive object_merge with list_merge shallow/deep/merge modes. Required observable cases include object merge nested dict; object merge list shallow; object merge list deep path.
- **B002**: The extracted feature must support this observable behavior: Dynaconf loads layered TOML settings files with environment sections. Required observable cases include dynaconf toml and env override; layered toml environments; merge multiple settings files.
- **B003**: The extracted feature must support this observable behavior: envvar_prefix overrides nested keys with precedence over file values. Required observable cases include object merge list shallow.
- **B004**: The extracted feature must support this observable behavior: merge_enabled combines multiple settings files. Required observable cases include merge multiple settings files.
- **B005**: The package exposes the required task API paths `featurelifted.Dynaconf`, `featurelifted.Dynaconf.BAR`, `featurelifted.Dynaconf.FOO`, `featurelifted.Dynaconf.HOST`, `featurelifted.Dynaconf.LIST`, `featurelifted.Dynaconf.PORT`, `featurelifted.Dynaconf.setenv`, `featurelifted.object_merge` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_object_merge_nested_dict`

- mapping: `B001`
- API: `featurelifted.object_merge`
- risk: `none`
- A001 `assert` L13: `merged == {'db': {'host': 'localhost', 'port': 3306, 'user': 'root'}, 'items': [1, 2, 3]}`

### `public_tests/test_public_api.py::test_dynaconf_toml_and_env_override`

- mapping: `B002`
- API: `featurelifted.Dynaconf`
- risk: `environment_state, filesystem_resource`
- A001 `assert` L29: `settings.HOST == 'localhost'`
- A002 `assert` L30: `settings.PORT == 8080`

### `hidden_tests/test_hidden_behavior.py::test_object_merge_list_shallow`

- mapping: `B001, B003`
- API: `featurelifted.object_merge`
- risk: `none`
- A001 `assert` L13: `merged['items'] == [9]`

### `hidden_tests/test_hidden_behavior.py::test_object_merge_list_deep_path`

- mapping: `B001`
- API: `featurelifted.object_merge`
- risk: `filesystem_resource`
- A001 `assert` L20: `merged['groups'][0]['ids'] == [3]`

### `hidden_tests/test_hidden_behavior.py::test_layered_toml_environments`

- mapping: `B002`
- API: `featurelifted.Dynaconf`
- risk: `environment_state, filesystem_resource`
- A001 `assert` L34: `settings.HOST == 'localhost'`
- A002 `assert` L35: `settings.PORT == 3000`

### `hidden_tests/test_hidden_behavior.py::test_merge_multiple_settings_files`

- mapping: `B002, B004`
- API: `featurelifted.Dynaconf`
- risk: `environment_state, filesystem_resource`
- A001 `assert` L51: `settings.FOO == 1`
- A002 `assert` L52: `settings.BAR == 2`
- A003 `assert` L53: `settings.LIST == [1, 2]`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.Dynaconf, featurelifted.object_merge`
- risk: `none`
- A001 `assert` L10: `isinstance(Dynaconf, type)`
- A002 `assert` L11: `Dynaconf is not None`
- A003 `assert` L12: `Dynaconf is not None`
- A004 `assert` L13: `Dynaconf is not None`
- A005 `assert` L14: `Dynaconf is not None`
- A006 `assert` L15: `Dynaconf is not None`
- A007 `assert` L16: `Dynaconf is not None`
- A008 `assert` L17: `callable(object_merge)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `dynaconf`
- source entrypoints: `dynaconf.utils.object_merge, dynaconf.Dynaconf, dynaconf.base.LazySettings, dynaconf.loaders.settings_loader, dynaconf.loaders.env_loader`
- oracle source files: `none`
- runtime dependencies: `none`
- oracle notes: Oracle copies merge core, loaders, and minimal vendor (box/toml); excludes contrib/cli/typed.
