# FeatureLift Task: Option groups and layered configuration

Build a standalone `featurelifted` package providing option registration, groups, defaults, INI file loading, and CLI precedence.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    ConfigOpts,
    Opt,
    OptGroup,
)
```

## Required API Details

- `ConfigOpts()` class constructor
  - `ConfigOpts.__call__(self, args=None, project=None, prog=None, version=None, usage=None, default_config_files=None, default_config_dirs=None, validate_default_values=False, description=None, epilog=None, use_env=True) -> None`
  - `ConfigOpts.register_opt(self, opt: Opt, group: str | OptGroup | None = None, cli: bool = False) -> bool`
  - `ConfigOpts.register_group(self, group: OptGroup) -> None`
  - `ConfigOpts.__getattr__(self, name: str) -> Any`
- `Opt(name: str, type=None, dest=None, short=None, default=None, positional=False, metavar=None, help=None, secret=False, required=None, deprecated_name=None, deprecated_group=None, deprecated_opts=None, sample_default=None, deprecated_for_removal=False, deprecated_reason=None, deprecated_since=None, mutable=False, advanced=False)` class constructor
  - `Opt.__init__(self, name: str, type=None, dest=None, short=None, default=None, positional=False, metavar=None, help=None, secret=False, required=None, deprecated_name=None, deprecated_group=None, deprecated_opts=None, sample_default=None, deprecated_for_removal=False, deprecated_reason=None, deprecated_since=None, mutable=False, advanced=False)`
- `OptGroup(name: str, title: str | None = None, help: str | None = None, dynamic_group_owner: str = "", driver_option: str = "")` class constructor
  - `OptGroup.__init__(self, name: str, title: str | None = None, help: str | None = None, dynamic_group_owner: str = "", driver_option: str = "")`

## Required Behavior

- Registering an `Opt` with `ConfigOpts.register_opt` makes its declared default available as an attribute before and after parsing with an empty argument list.
- Registering an `OptGroup` and a grouped `Opt` makes the value available through `config.<group>.<option>`, while default-group options remain available directly on the `ConfigOpts` object.
- When a registered option is present in an INI configuration file supplied with `--config-file`, parsing loads the file value, including values in named option-group sections.
- When an option is registered with `cli=True`, a command-line value overrides both its declared default and a value from a supplied configuration file; options not overridden on the command line retain their file or default values.
- The package exposes all required `ConfigOpts`, `Opt`, `OptGroup`, registration, parsing, and attribute-access paths with the callable signatures listed in this contract.
- The submitted package does not import the forbidden upstream package `oslo_config`.

## Constraints

- Forbidden imports: `oslo_config`.
- Do not implement remote configuration source plugins.
- Do not implement sample configuration generation.
- Do not implement OpenStack service integration.
- Do not implement runtime import of oslo_config.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — Registering an `Opt` with `ConfigOpts.register_opt` makes its declared default available as an attribute before and after parsing with an empty argument list.
- **B002** — Registering an `OptGroup` and a grouped `Opt` makes the value available through `config.<group>.<option>`, while default-group options remain available directly on the `ConfigOpts` object.
- **B003** — When a registered option is present in an INI configuration file supplied with `--config-file`, parsing loads the file value, including values in named option-group sections.
- **B004** — When an option is registered with `cli=True`, a command-line value overrides both its declared default and a value from a supplied configuration file; options not overridden on the command line retain their file or default values.
- **B005** — The package exposes all required `ConfigOpts`, `Opt`, `OptGroup`, registration, parsing, and attribute-access paths with the callable signatures listed in this contract.
- **B006** — The submitted package does not import the forbidden upstream package `oslo_config`.
<!-- featureliftbench:behavior-clauses:end -->
