# FeatureLift Task: Config find and merge

Build a standalone `featurelifted` package that finds pylint config files and merges disable/unknown options into a `PyLinter` without running a full lint of pylint itself.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    find_default_config_files,
    PyLinter,
    UnrecognizedOptionError,
)
```

## Required API Details

- `find_default_config_files() -> Iterator[Path]`
- `PyLinter(options=(), reporter=None, option_groups=(), pylintrc=None)` class constructor
  - `PyLinter.__init__(self, options=(), reporter=None, option_groups=(), pylintrc=None) -> None`
  - `PyLinter.load_default_plugins(self) -> None`
  - `PyLinter.is_message_enabled(self, msg_descr: str, line: int | None = None, confidence=None) -> bool`
  - `PyLinter._parse_command_line_configuration(self, arguments: Sequence[str] | None = None) -> list[str]`
  - `PyLinter._parse_configuration_file(self, arguments: list[str]) -> None`
- `UnrecognizedOptionError` must be importable and raisable

## Required Behavior

- When the current working directory contains a `pylintrc` file, `find_default_config_files()` yields that path; when `PYLINTRC` points at an existing file, that path is also yielded.
- After `load_default_plugins`, `is_message_enabled('unused-import')` is True, and `_parse_command_line_configuration(['--disable=unused-import'])` makes it False while leaving unrelated messages enabled.
- Calling `_parse_configuration_file(['--disable=unused-import'])` after loading default plugins makes `is_message_enabled('unused-import')` False.
- Parsing a configuration argument that is not a pylint option raises `UnrecognizedOptionError` whose `options` list contains the option name without the leading dashes.
- The package exposes `find_default_config_files`, `PyLinter`, and `UnrecognizedOptionError` with the callable signatures listed in this contract.
- The submitted package source does not import the forbidden upstream package `pylint`.

## Constraints

- Forbidden imports: `pylint`.
- Do not implement full lint of pylint itself.
- Do not implement parallel checker execution.
- Do not implement HTML reports.
- Do not implement runtime import of pylint.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — When the current working directory contains a `pylintrc` file, `find_default_config_files()` yields that path; when `PYLINTRC` points at an existing file, that path is also yielded.
- **B002** — After `load_default_plugins`, `is_message_enabled('unused-import')` is True, and `_parse_command_line_configuration(['--disable=unused-import'])` makes it False while leaving unrelated messages enabled.
- **B003** — Calling `_parse_configuration_file(['--disable=unused-import'])` after loading default plugins makes `is_message_enabled('unused-import')` False.
- **B004** — Parsing a configuration argument that is not a pylint option raises `UnrecognizedOptionError` whose `options` list contains the option name without the leading dashes.
- **B005** — The package exposes `find_default_config_files`, `PyLinter`, and `UnrecognizedOptionError` with the callable signatures listed in this contract.
- **B006** — The submitted package source does not import the forbidden upstream package `pylint`.
<!-- featureliftbench:behavior-clauses:end -->
