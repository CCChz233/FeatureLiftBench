# FeatureLift Task: Git config parse

Build a standalone `featurelifted` package that parses Git config files like Dulwich `ConfigFile`, including subsections and booleans, without speaking the Git protocol.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    ConfigFile,
)
```

## Required API Details

- `ConfigFile()` class constructor
  - `ConfigFile.from_file(cls, f, *, expand_includes=True)`
  - `ConfigFile.from_path(cls, path, *, expand_includes=True)`
  - `ConfigFile.get(self, section, name)`
  - `ConfigFile.get_boolean(self, section, name)`

## Required Behavior

- `ConfigFile.from_file` on a buffer containing `[core]` / `filemode = true` yields `get((b"core",), b"filemode") == b"true"` when `expand_includes=False`.
- A `[remote "origin"]` `url` setting is readable with `get((b"remote", b"origin"), b"url")`.
- `get_boolean((b"core",), b"filemode")` is True for `filemode = true`.
- `get` on a missing key raises `KeyError`.
- The package exposes `ConfigFile` with `from_file`, `from_path`, `get`, and `get_boolean`.
- The submitted package source does not import the forbidden upstream package `dulwich`.

## Constraints

- Forbidden imports: `dulwich`.
- Do not implement git protocol.
- Do not implement pack files.
- Do not implement network.
- Do not implement runtime import of dulwich.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — `ConfigFile.from_file` on a buffer containing `[core]` / `filemode = true` yields `get((b"core",), b"filemode") == b"true"` when `expand_includes=False`.
- **B002** — A `[remote "origin"]` `url` setting is readable with `get((b"remote", b"origin"), b"url")`.
- **B003** — `get_boolean((b"core",), b"filemode")` is True for `filemode = true`.
- **B004** — `get` on a missing key raises `KeyError`.
- **B005** — The package exposes `ConfigFile` with `from_file`, `from_path`, `get`, and `get_boolean`.
- **B006** — The submitted package source does not import the forbidden upstream package `dulwich`.
<!-- featureliftbench:behavior-clauses:end -->
