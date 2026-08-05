# jupyter_core__paths_resolver_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `8/20`

## Required API

- `featurelifted.jupyter_config_dir` (function) `(env: 'Mapping[str, str] | None' = None, home: 'str | None' = None, platform: 'str' = 'linux') -> 'str'`
- `featurelifted.jupyter_config_path` (function) `(env: 'Mapping[str, str] | None' = None, home: 'str | None' = None, platform: 'str' = 'linux', sys_prefix: 'str' = '/usr', user_site_base: 'str | None' = None, enable_user_site: 'bool' = True) -> 'list[str]'`
- `featurelifted.jupyter_data_dir` (function) `(env: 'Mapping[str, str] | None' = None, home: 'str | None' = None, platform: 'str' = 'linux') -> 'str'`
- `featurelifted.jupyter_path` (function) `(*subdirs: 'str', env: 'Mapping[str, str] | None' = None, home: 'str | None' = None, platform: 'str' = 'linux', sys_prefix: 'str' = '/usr', user_site_base: 'str | None' = None, enable_user_site: 'bool' = True) -> 'list[str]'`
- `featurelifted.jupyter_runtime_dir` (function) `(env: 'Mapping[str, str] | None' = None, home: 'str | None' = None, platform: 'str' = 'linux') -> 'str'`

## Public Behaviors

- **B001**: When JUPYTER_CONFIG_PATH or JUPYTER_PATH is set, its entries are ordered ahead of the applicable default search paths.
- **B002**: When JUPYTER_CONFIG_DIR, JUPYTER_DATA_DIR, or JUPYTER_RUNTIME_DIR is set, the corresponding resolver returns that explicit directory.
- **B003**: Without overrides, the path resolvers return deterministic Linux, macOS, and Windows user and system defaults for the selected platform.
- **B004**: When JUPYTER_NO_CONFIG is enabled, normal user and environment config paths are suppressed according to isolated-config behavior.
- **B005**: When JUPYTER_PREFER_ENV_PATH changes preference, environment-level paths move before or after user paths without dropping either group.
- **B006**: The package exposes the required task API paths `featurelifted.jupyter_config_dir`, `featurelifted.jupyter_config_path`, `featurelifted.jupyter_data_dir`, `featurelifted.jupyter_path`, `featurelifted.jupyter_runtime_dir` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_config_env_path_precedes_user_path`

- mapping: `B001, B005`
- API: `featurelifted.jupyter_config_path`
- risk: `filesystem_resource`
- A001 `assert` L7: `paths[:2] == ['/env/etc', '/more/etc']`
- A002 `assert` L8: `'/home/alice/.jupyter' in paths`
- A003 `assert` L9: `'/usr/etc/jupyter' in paths`

### `public_tests/test_public_contract.py::test_data_path_adds_requested_subdir`

- mapping: `B003, B005`
- API: `featurelifted.jupyter_path`
- risk: `filesystem_resource`
- A001 `assert` L15: `paths[0] == '/xdg/data/jupyter/kernels'`
- A002 `assert` L16: `paths[-2:] == ['/usr/local/share/jupyter/kernels', '/usr/share/jupyter/kernels']`

### `public_tests/test_public_contract.py::test_data_dir_platform_defaults`

- mapping: `B002`
- API: `featurelifted.jupyter_data_dir`
- risk: `none`
- A001 `assert` L23: `jupyter_data_dir(env={}, home='/Users/alice', platform='darwin') == '/Users/alice/Library/Jupyter'`
- A002 `assert` L24: `jupyter_data_dir(env={'APPDATA': 'C:\\Users\\Alice\\AppData\\Roaming'}, home='C:\\Users\\Alice', platform='win32') == 'C:\\Users\\Alice\\AppData\\Roaming\\jupyter'`

### `hidden_tests/test_hidden_contract.py::test_hidden_runtime_dir_env_override_and_xdg_fallback`

- mapping: `B002`
- API: `featurelifted.jupyter_path, featurelifted.jupyter_runtime_dir`
- risk: `filesystem_resource`
- A001 `assert` L10: `jupyter_path(env=env, home='/home/a', platform='linux')[:2] == ['/one', '/two']`
- A002 `assert` L11: `jupyter_runtime_dir(env=env, home='/home/a', platform='linux') == '/runtime'`

### `hidden_tests/test_hidden_contract.py::test_hidden_prefer_environment_over_user_changes_order`

- mapping: `B005`
- API: `featurelifted.jupyter_config_path`
- risk: `filesystem_resource, ordering_semantics`
- A001 `assert` L17: `paths[:3] == ['/opt/venv/etc/jupyter', '/home/a/.jupyter', '/home/a/.local/etc/jupyter']`

### `hidden_tests/test_hidden_contract.py::test_hidden_no_config_uses_clean_config_dir_only`

- mapping: `B002`
- API: `featurelifted.jupyter_config_dir, featurelifted.jupyter_config_path`
- risk: `filesystem_resource`
- A001 `assert` L22: `jupyter_config_dir(env=env, home='/home/a', platform='linux') == '__JUPYTER_NO_CONFIG_TEMP__'`
- A002 `assert` L23: `jupyter_config_path(env=env, home='/home/a', platform='linux') == ['__JUPYTER_NO_CONFIG_TEMP__']`

### `hidden_tests/test_hidden_contract.py::test_hidden_windows_path_separator_and_programdata_default`

- mapping: `B001, B003, B004`
- API: `featurelifted.jupyter_path`
- risk: `filesystem_resource`
- A001 `assert` L29: `paths[:2] == ['C:\\one', 'C:\\two']`
- A002 `assert` L30: `'C:\\Py\\share\\jupyter' in paths`
- A003 `assert` L31: `'/usr/share/jupyter' not in paths`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.jupyter_config_dir, featurelifted.jupyter_config_path, featurelifted.jupyter_data_dir, featurelifted.jupyter_path, featurelifted.jupyter_runtime_dir`
- risk: `none`
- A001 `assert` L13: `callable(jupyter_config_dir)`
- A002 `assert` L14: `callable(jupyter_config_path)`
- A003 `assert` L15: `callable(jupyter_data_dir)`
- A004 `assert` L16: `callable(jupyter_path)`
- A005 `assert` L17: `callable(jupyter_runtime_dir)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `jupyter_core, platformdirs`
- source entrypoints: `jupyter_core.paths.jupyter_config_dir, jupyter_core.paths.jupyter_data_dir, jupyter_core.paths.jupyter_runtime_dir, jupyter_core.paths.jupyter_path, jupyter_core.paths.jupyter_config_path`
- oracle source files: `reference_solution/featurelifted/__init__.py`
- runtime dependencies: `none`
- oracle notes: Materialized compact oracle for the selected Jupyter path resolver behavior.
