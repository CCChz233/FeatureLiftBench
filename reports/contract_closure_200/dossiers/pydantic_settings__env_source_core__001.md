# pydantic_settings__env_source_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `6/10`

## Required API

- `featurelifted.BaseSettings` (class) `(_case_sensitive: 'bool | None' = None, _nested_model_default_partial_update: 'bool | None' = None, _env_prefix: 'str | None' = None, _env_prefix_target: 'EnvPrefixTarget | None' = None, _env_file: 'DotenvType | None' = PosixPath('.'), _env_file_encoding: 'str | None' = None, _env_ignore_empty: 'bool | None' = None, _env_nested_delimiter: 'str | None' = None, _env_nested_max_split: 'int | None' = None, _env_parse_none_str: 'str | None' = None, _env_parse_enums: 'bool | None' = None, _cli_prog_name: 'str | None' = None, _cli_parse_args: 'bool | list[str] | tuple[str, ...] | None' = None, _cli_settings_source: 'CliSettingsSource[Any] | None' = None, _cli_parse_none_str: 'str | None' = None, _cli_hide_none_type: 'bool | None' = None, _cli_avoid_json: 'bool | None' = None, _cli_enforce_required: 'bool | None' = None, _cli_use_class_docs_for_groups: 'bool | None' = None, _cli_exit_on_error: 'bool | None' = None, _cli_prefix: 'str | None' = None, _cli_flag_prefix_char: 'str | None' = None, _cli_implicit_flags: "bool | Literal['dual', 'toggle'] | None" = None, _cli_ignore_unknown_args: 'bool | None' = None, _cli_kebab_case: "bool | Literal['all', 'no_enums'] | None" = None, _cli_shortcuts: 'Mapping[str, str | list[str]] | None' = None, _secrets_dir: 'PathType | None' = None, _build_sources: 'tuple[tuple[PydanticBaseSettingsSource, ...], dict[str, Any]] | None' = None) -> None`
- `featurelifted.SettingsConfigDict` (class) `(*args, **kwargs)`
- `featurelifted.SettingsError` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: BaseSettings loads fields from os.environ with env_prefix. Required observable cases include env prefix and nested; parse none str.
- **B002**: The extracted feature must support this observable behavior: nested models via env_nested_delimiter. Required observable cases include env prefix and nested; parse none str.
- **B003**: The extracted feature must support this observable behavior: json/complex field parsing and case_sensitive option. Required observable cases include json list env; case sensitive env.
- **B004**: The extracted feature must support this observable behavior: env_ignore_empty and env_parse_none_str. Required observable cases include json list env; ignore empty env; parse none str.
- **B005**: The package exposes the required task API paths `featurelifted.BaseSettings`, `featurelifted.SettingsConfigDict`, `featurelifted.SettingsError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_env_prefix_and_nested`

- mapping: `B001, B002`
- API: `none detected`
- risk: `environment_state`
- A001 `assert` L22: `settings.port == 9000`
- A002 `assert` L23: `settings.debug is True`
- A003 `assert` L24: `settings.db == {'host': 'db.internal'}`

### `hidden_tests/test_hidden_behavior.py::test_json_list_env`

- mapping: `B003, B004`
- API: `none detected`
- risk: `environment_state`
- A001 `assert` L20: `settings.tags == ['a', 'b']`

### `hidden_tests/test_hidden_behavior.py::test_case_sensitive_env`

- mapping: `B003`
- API: `featurelifted.BaseSettings, featurelifted.SettingsConfigDict`
- risk: `environment_state`
- A001 `assert` L29: `CaseSettings().MyField == 'ok'`

### `hidden_tests/test_hidden_behavior.py::test_ignore_empty_env`

- mapping: `B004`
- API: `featurelifted.BaseSettings, featurelifted.SettingsConfigDict`
- risk: `environment_state`
- A001 `assert` L38: `EmptySettings().name == 'default'`

### `hidden_tests/test_hidden_behavior.py::test_parse_none_str`

- mapping: `B001, B002, B004`
- API: `featurelifted.BaseSettings, featurelifted.SettingsConfigDict`
- risk: `environment_state`
- A001 `assert` L47: `NoneSettings().value is None`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.BaseSettings, featurelifted.SettingsConfigDict, featurelifted.SettingsError`
- risk: `none`
- A001 `assert` L11: `isinstance(BaseSettings, type)`
- A002 `assert` L12: `isinstance(SettingsConfigDict, type)`
- A003 `assert` L13: `issubclass(SettingsError, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `annotated-types, pydantic, pydantic-core, typing-extensions, typing-inspection`
- forbidden imports: `pydantic_settings`
- source entrypoints: `pydantic_settings.BaseSettings, pydantic_settings.sources.EnvSettingsSource, pydantic_settings.sources.utils.parse_env_vars, pydantic_settings.SettingsConfigDict`
- oracle source files: `none`
- runtime dependencies: `none`
- oracle notes: Oracle copies BaseSettings and EnvSettingsSource closure; repo retains all providers for copy-all.
