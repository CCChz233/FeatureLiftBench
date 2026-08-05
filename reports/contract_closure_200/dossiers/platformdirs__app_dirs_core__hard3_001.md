# platformdirs__app_dirs_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `9/25`

## Required API

- `featurelifted.user_cache_dir` (function) `(appname: 'str | None' = None, appauthor: 'str | bool | None' = None, version: 'str | None' = None, opinion: 'bool' = True, platform: 'str' = 'linux', env: 'Env' = None, home: 'str | None' = None) -> 'str'`
- `featurelifted.user_config_dir` (function) `(appname: 'str | None' = None, appauthor: 'str | bool | None' = None, version: 'str | None' = None, roaming: 'bool' = False, platform: 'str' = 'linux', env: 'Env' = None, home: 'str | None' = None) -> 'str'`
- `featurelifted.user_data_dir` (function) `(appname: 'str | None' = None, appauthor: 'str | bool | None' = None, version: 'str | None' = None, roaming: 'bool' = False, platform: 'str' = 'linux', env: 'Env' = None, home: 'str | None' = None) -> 'str'`

## Public Behaviors

- **B001**: `XDG_DATA_HOME`, `XDG_CONFIG_HOME`, and `XDG_CACHE_HOME` override defaults when they are non-blank.
- **B002**: Defaults are `~/.local/share`, `~/.config`, and `~/.cache`.
- **B003**: On macOS, data and config paths default to Library/Application Support and cache paths default to Library/Caches under home.
- **B004**: On macOS, non-blank XDG directory overrides take precedence over the Library defaults.
- **B005**: Data/config use `LOCALAPPDATA` by default and `APPDATA` when `roaming=True`.
- **B006**: On Windows, appauthor, appauthor=False, version, roaming, and cache opinion options determine the exact appended path segments.
- **B007**: The package exposes the required task API paths `featurelifted.user_cache_dir`, `featurelifted.user_config_dir`, `featurelifted.user_data_dir` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_linux_defaults_append_app_and_version`

- mapping: `B002`
- API: `featurelifted.user_cache_dir, featurelifted.user_config_dir, featurelifted.user_data_dir`
- risk: `none`
- A001 `assert` L5: `user_data_dir('demo', version='2', platform='linux', home='/home/alice', env={}) == '/home/alice/.local/share/demo/2'`
- A002 `assert` L8: `user_config_dir('demo', platform='linux', home='/home/alice', env={}) == '/home/alice/.config/demo'`
- A003 `assert` L9: `user_cache_dir('demo', platform='linux', home='/home/alice', env={}) == '/home/alice/.cache/demo'`

### `public_tests/test_public_contract.py::test_linux_xdg_overrides_take_precedence`

- mapping: `B001, B004`
- API: `featurelifted.user_cache_dir, featurelifted.user_config_dir, featurelifted.user_data_dir`
- risk: `none`
- A001 `assert` L18: `user_data_dir('tool', platform='linux', home='/home/alice', env=env) == '/srv/data/tool'`
- A002 `assert` L19: `user_config_dir('tool', platform='linux', home='/home/alice', env=env) == '/srv/config/tool'`
- A003 `assert` L20: `user_cache_dir('tool', platform='linux', home='/home/alice', env=env) == '/srv/cache/tool'`

### `public_tests/test_public_contract.py::test_windows_author_roaming_and_cache_layout`

- mapping: `B005, B006`
- API: `featurelifted.user_cache_dir, featurelifted.user_data_dir`
- risk: `state_mutation`
- A001 `assert` L28: `user_data_dir('App', appauthor='Vendor', platform='windows', env=env) == 'C:\\Users\\Alice\\AppData\\Local\\Vendor\\App'`
- A002 `assert` L31: `user_data_dir('App', appauthor='Vendor', roaming=True, platform='windows', env=env) == 'C:\\Users\\Alice\\AppData\\Roaming\\Vendor\\App'`
- A003 `assert` L34: `user_cache_dir('App', appauthor='Vendor', version='1.0', platform='windows', env=env) == 'C:\\Users\\Alice\\AppData\\Local\\Vendor\\App\\Cache\\1.0'`

### `hidden_tests/test_hidden_contract.py::test_macos_defaults_and_xdg_precedence`

- mapping: `B001, B004`
- API: `featurelifted.user_config_dir, featurelifted.user_data_dir`
- risk: `none`
- A001 `assert` L5: `user_data_dir('Notebook', platform='darwin', home='/Users/ada', env={}) == '/Users/ada/Library/Application Support/Notebook'`
- A002 `assert` L8: `user_config_dir('Notebook', version='7', platform='macos', home='/Users/ada', env={}) == '/Users/ada/Library/Application Support/Notebook/7'`
- A003 `assert` L12: `user_data_dir('Notebook', platform='macos', home='/Users/ada', env=env) == '/Volumes/xdg-data/Notebook'`
- A004 `assert` L13: `user_config_dir('Notebook', platform='macos', home='/Users/ada', env=env) == '/Volumes/xdg-config/Notebook'`

### `hidden_tests/test_hidden_contract.py::test_blank_xdg_values_are_ignored`

- mapping: `B001, B004`
- API: `featurelifted.user_cache_dir, featurelifted.user_config_dir, featurelifted.user_data_dir`
- risk: `none`
- A001 `assert` L20: `user_data_dir('tool', version='v2', platform='linux', home='/home/bob', env=env) == '/home/bob/.local/share/tool/v2'`
- A002 `assert` L23: `user_config_dir('tool', platform='linux', home='/home/bob', env=env) == '/home/bob/.config/tool'`
- A003 `assert` L24: `user_cache_dir('tool', platform='linux', home='/home/bob', env=env) == '/home/bob/.cache/tool'`

### `hidden_tests/test_hidden_contract.py::test_windows_appauthor_false_omits_author_segment`

- mapping: `B006`
- API: `featurelifted.user_config_dir, featurelifted.user_data_dir`
- risk: `none`
- A001 `assert` L29: `user_data_dir('App', appauthor=False, version='3', platform='win32', env=env) == 'D:\\Local\\App\\3'`
- A002 `assert` L30: `user_config_dir('App', appauthor=False, roaming=True, platform='windows', env=env) == 'D:\\Roaming\\App'`

### `hidden_tests/test_hidden_contract.py::test_windows_cache_opinion_can_be_disabled`

- mapping: `B002, B003, B005, B006`
- API: `featurelifted.user_cache_dir`
- risk: `state_mutation`
- A001 `assert` L35: `user_cache_dir('App', appauthor='Vendor', version='2', platform='windows', env=env, opinion=False) == 'C:\\Local\\Vendor\\App\\2'`

### `hidden_tests/test_hidden_contract.py::test_no_appname_returns_platform_base_dir`

- mapping: `B007`
- API: `featurelifted.user_cache_dir, featurelifted.user_data_dir`
- risk: `none`
- A001 `assert` L41: `user_data_dir(platform='linux', home='/home/chris', env={}) == '/home/chris/.local/share'`
- A002 `assert` L42: `user_cache_dir(platform='macos', home='/Users/chris', env={}) == '/Users/chris/Library/Caches'`
- A003 `assert` L43: `user_data_dir(platform='windows', home='C:\\Users\\Chris', env={}) == 'C:\\Users\\Chris\\AppData\\Local'`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B007`
- API: `featurelifted.user_cache_dir, featurelifted.user_config_dir, featurelifted.user_data_dir`
- risk: `none`
- A001 `assert` L11: `callable(user_cache_dir)`
- A002 `assert` L12: `callable(user_config_dir)`
- A003 `assert` L13: `callable(user_data_dir)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `platformdirs`
- source entrypoints: `platformdirs.user_data_dir, platformdirs.user_config_dir, platformdirs.user_cache_dir`
- oracle source files: `repo/src/platformdirs/__init__.py, repo/src/platformdirs/api.py, repo/src/platformdirs/_xdg.py, repo/src/platformdirs/unix.py, repo/src/platformdirs/macos.py, repo/src/platformdirs/windows.py`
- runtime dependencies: `none`
- oracle notes: Task-scoped extraction of user data/config/cache path resolution. Site, media, Android, and directory creation helpers are intentionally excluded.
