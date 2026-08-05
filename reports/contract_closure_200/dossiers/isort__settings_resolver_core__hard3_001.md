# isort__settings_resolver_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `9/26`

## Required API

- `featurelifted.ProfileDoesNotExist` (exception)
- `featurelifted.UnsupportedSettings` (exception)
- `featurelifted.Settings` (class) `(line_length: 'int' = 79, multi_line_output: 'int' = 0, include_trailing_comma: 'bool' = False, split_on_trailing_comma: 'bool' = False, force_grid_wrap: 'int' = 0, use_parentheses: 'bool' = False, ensure_newline_before_comments: 'bool' = False, combine_as_imports: 'bool' = False, force_single_line: 'bool' = False, force_sort_within_sections: 'bool' = False, lexicographical: 'bool' = False, order_by_type: 'bool' = True, group_by_package: 'bool' = False, skip: 'frozenset[str]' = frozenset({'.pants.d', '_build', '.mypy_cache', '.svn', '.eggs', '.git', '.direnv', '.hg', 'node_modules', 'dist', '.tox', '.bzr', '.venv', 'buck-out', '.nox', 'build'}), extend_skip: 'frozenset[str]' = frozenset(), skip_glob: 'frozenset[str]' = frozenset(), extend_skip_glob: 'frozenset[str]' = frozenset(), src_paths: 'tuple[Path, ...]' = (), directory: 'Path' = <factory>, profile: 'str' = '', source: 'str' = 'defaults', sources: 'tuple[str, ...]' = ('defaults',)) -> None`
- `featurelifted.Settings.line_length` (attribute)
- `featurelifted.Settings.src_paths` (attribute)
- `featurelifted.resolve_settings` (function) `(config_files=(), profile: 'str | None' = None, overrides: 'dict[str, Any] | None' = None) -> 'Settings'`
- `featurelifted.resolve_from_path` (function) `(start_path: 'str | Path', profile: 'str | None' = None, overrides: 'dict[str, Any] | None' = None) -> 'Settings'`
- `featurelifted.find_config` (function) `(start_path: 'str | Path') -> 'Path | None'`
- `featurelifted.should_skip` (function) `(path: 'str | Path', settings: 'Settings') -> 'bool'`
- `featurelifted.Settings.is_skipped` (method) `(self, path: 'str | Path') -> 'bool'`

## Public Behaviors

- **B001**: When config files, profile, and runtime overrides are supplied, resolve_settings returns a Settings object whose fields reflect defaults, then profile, then config files, then overrides.
- **B002**: When resolve_from_path is called from a file path, it discovers the nearest applicable config and returns Settings resolved from that discovery chain.
- **B003**: When find_config is called from a start path, it returns the nearest config file path used by isort or None when no config exists.
- **B004**: When should_skip is called with a path and Settings, it returns True only for paths matching explicit skip names or glob patterns.
- **B005**: When Settings.is_skipped is called, it applies the same skip-name and glob rules as should_skip for that Settings instance.
- **B006**: When black, django, or google profiles are selected, the resulting Settings expose the profile-specific defaults expected by isort.
- **B007**: When pyproject.toml, setup.cfg, tox.ini, .isort.cfg, or .editorconfig sections are present, their isort-relevant options are parsed into Settings.
- **B008**: When runtime overrides are provided, they override profile and config-file values in the resolved Settings object.
- **B009**: When src_paths are configured, they are expanded relative to the config file directory in the resolved Settings object.
- **B010**: When skip, extend_skip, skip_glob, or extend_skip_glob are configured, the effective skip rules merge extend lists and still allow existing non-matching files to remain unskipped.
- **B011**: The package exposes the required task API paths `featurelifted.ProfileDoesNotExist`, `featurelifted.UnsupportedSettings`, `featurelifted.Settings`, `featurelifted.Settings.line_length`, `featurelifted.Settings.src_paths`, `featurelifted.resolve_settings`, `featurelifted.resolve_from_path`, `featurelifted.find_config`, `featurelifted.should_skip`, `featurelifted.Settings.is_skipped` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_profile_and_pyproject_merge`

- mapping: `B006, B007`
- API: `featurelifted.resolve_settings, featurelifted.should_skip`
- risk: `filesystem_resource`
- A001 `assert` L10: `settings.profile == 'black'`
- A002 `assert` L11: `settings.line_length == 88`
- A003 `assert` L12: `should_skip(tmp_path / 'build' / 'x.py', settings)`
- A004 `assert` L13: `settings.is_skipped(tmp_path / 'build' / 'x.py')`

### `public_tests/test_public_contract.py::test_runtime_overrides_win_over_profile_and_config`

- mapping: `B008`
- API: `featurelifted.resolve_settings`
- risk: `filesystem_resource`
- A001 `assert` L22: `settings.line_length == 120`
- A002 `assert` L23: `settings.include_trailing_comma is True`

### `public_tests/test_public_contract.py::test_resolve_from_path_finds_nearest_pyproject`

- mapping: `B002`
- API: `featurelifted.resolve_from_path`
- risk: `filesystem_resource`
- A001 `assert` L33: `settings.profile == 'django'`
- A002 `assert` L34: `settings.combine_as_imports is True`

### `hidden_tests/test_hidden_contract.py::test_extend_skip_glob_and_existing_file_not_skipped`

- mapping: `B004, B005, B010`
- API: `featurelifted.resolve_settings, featurelifted.should_skip`
- risk: `filesystem_resource`
- A001 `assert` L17: `should_skip(tmp_path / 'generated' / 'client.py', settings)`
- A002 `assert` L18: `not should_skip(target, settings)`

### `hidden_tests/test_hidden_contract.py::test_src_paths_are_resolved_relative_to_config_dir`

- mapping: `B002, B009`
- API: `featurelifted.resolve_settings`
- risk: `filesystem_resource`
- A001 `assert` L29: `settings.src_paths == ((tmp_path / 'src').resolve(), (tmp_path / 'lib').resolve())`

### `hidden_tests/test_hidden_contract.py::test_setup_cfg_and_pyproject_precedence_follows_input_order`

- mapping: `B001, B007`
- API: `featurelifted.resolve_settings`
- risk: `filesystem_resource, ordering_semantics`
- A001 `assert` L38: `resolve_settings([setup_cfg, pyproject]).line_length == 110`
- A002 `assert` L39: `resolve_settings([pyproject, setup_cfg]).line_length == 90`

### `hidden_tests/test_hidden_contract.py::test_invalid_profile_and_unsupported_setting_errors`

- mapping: `B006`
- API: `featurelifted.ProfileDoesNotExist, featurelifted.UnsupportedSettings, featurelifted.resolve_settings`
- risk: `exception_semantics, filesystem_resource`
- A001 `raises` L46: `pytest.raises(ProfileDoesNotExist)`
- A002 `raises` L48: `pytest.raises(UnsupportedSettings)`

### `hidden_tests/test_hidden_contract.py::test_editorconfig_indent_and_line_length`

- mapping: `B003, B007, B008`
- API: `featurelifted.resolve_settings`
- risk: `filesystem_resource`
- A001 `assert` L58: `settings.line_length == 99`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B011`
- API: `featurelifted.ProfileDoesNotExist, featurelifted.Settings, featurelifted.UnsupportedSettings, featurelifted.find_config, featurelifted.resolve_from_path, featurelifted.resolve_settings, featurelifted.should_skip`
- risk: `none`
- A001 `assert` L15: `issubclass(ProfileDoesNotExist, BaseException)`
- A002 `assert` L16: `issubclass(UnsupportedSettings, BaseException)`
- A003 `assert` L17: `isinstance(Settings, type)`
- A004 `assert` L18: `Settings is not None`
- A005 `assert` L19: `Settings is not None`
- A006 `assert` L20: `callable(resolve_settings)`
- A007 `assert` L21: `callable(resolve_from_path)`
- A008 `assert` L22: `callable(find_config)`
- A009 `assert` L23: `callable(should_skip)`
- A010 `assert` L24: `callable(getattr(Settings, 'is_skipped'))`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `isort`
- source entrypoints: `isort.settings.Config, isort.settings._get_config_data, isort.settings._find_config, isort.settings.Config.is_skipped, isort.profiles.profiles`
- oracle source files: `repo/isort/settings.py, repo/isort/profiles.py, repo/isort/exceptions.py, repo/isort/files.py, repo/pyproject.toml, repo/LICENSE`
- runtime dependencies: `none`
- oracle notes: Task-scoped settings/profile resolver. Import sorting, formatter internals, CLI behavior, git integration, and entry point plugins are intentionally excluded.
