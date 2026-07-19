# FeatureLift Task: Environment settings source

Extract pydantic-settings BaseSettings env source with nested delimiter parsing without importing pydantic_settings.

## Target API

- Import: `from featurelifted import BaseSettings, SettingsConfigDict, SettingsError`
- Callable: `featurelifted.BaseSettings`
- Signature: `class Settings(BaseSettings): ...`

## Excluded Behavior

- dotenv, yaml/toml/json file sources and cloud secret providers
- CLI settings source and subcommand parsing
- original pydantic_settings import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `pydantic_settings`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — BaseSettings loads fields from os.environ with env_prefix
- **B002** — nested models via env_nested_delimiter
- **B003** — json/complex field parsing and case_sensitive option
- **B004** — env_ignore_empty and env_parse_none_str
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: pydantic_settings
<!-- featureliftbench:behavior-clauses:end -->
