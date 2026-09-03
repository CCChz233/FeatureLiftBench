# FeatureLift Task: Layered dict/env/path configuration

Build a standalone `featurelifted` package providing layered configuration from dictionaries, environment variables, and filesystem paths, with both item and attribute access.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    config_from_dict,
    config_from_env,
    config_from_path,
    Configuration,
    ConfigurationSet,
)
```

## Required API Details

- `Configuration(config_: Mapping[str, Any], lowercase_keys: bool = False)` class constructor
  - `Configuration.__init__(self, config_: Mapping[str, Any], lowercase_keys: bool = False)`
  - `Configuration.__getitem__(self, item: str) -> Union[ForwardRef('Configuration'), Any]`
  - `Configuration.y` attribute must exist on instances
- `ConfigurationSet(*configs: Configuration)` class constructor
  - `ConfigurationSet.__init__(self, *configs: Configuration)`
  - `ConfigurationSet.left` attribute must exist on instances
  - `ConfigurationSet.right` attribute must exist on instances
  - `ConfigurationSet.shared` attribute must exist on instances
- `config_from_dict(data: Mapping, *, lowercase_keys: bool = False) -> Configuration`
- `config_from_env(prefix: str, separator: str = '__', *, strip_prefix: bool = True) -> Configuration`
- `config_from_path(path: str, remove_level: int = 1) -> Configuration`

## Required Behavior

- Building a configuration from a nested dictionary exposes both item access and attribute access for the same keys, including one dotted nesting level such as a `db.host` value reachable as `cfg.db.host` and `cfg['db']['host']`.
- A `ConfigurationSet` built from two configurations prefers the first layer for overlapping keys and still returns keys that exist only in a later layer.
- `config_from_env(prefix)` includes environment variables whose names start with `prefix` plus the default `__` separator, strips that prefix, and turns remaining `__` segments into dotted keys.
- `config_from_path` reads files under a directory and exposes each file's text content as a configuration value whose key is derived from the relative path.
- Reading a key that is absent from every layer raises `KeyError`. The package exposes `Configuration`, `ConfigurationSet`, `config_from_dict`, `config_from_env`, and `config_from_path`.
- The submitted package source does not import the forbidden upstream package `config`.

## Constraints

- Forbidden imports: `config`.
- Do not implement cloud secret backends.
- Do not implement AWS/Azure/GCP/Vault contrib loaders.
- Do not implement runtime import of config.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — Building a configuration from a nested dictionary exposes both item access and attribute access for the same keys, including one dotted nesting level such as a `db.host` value reachable as `cfg.db.host` and `cfg['db']['host']`.
- **B002** — A `ConfigurationSet` built from two configurations prefers the first layer for overlapping keys and still returns keys that exist only in a later layer.
- **B003** — `config_from_env(prefix)` includes environment variables whose names start with `prefix` plus the default `__` separator, strips that prefix, and turns remaining `__` segments into dotted keys.
- **B004** — `config_from_path` reads files under a directory and exposes each file's text content as a configuration value whose key is derived from the relative path.
- **B005** — Reading a key that is absent from every layer raises `KeyError`. The package exposes `Configuration`, `ConfigurationSet`, `config_from_dict`, `config_from_env`, and `config_from_path`.
- **B006** — The submitted package source does not import the forbidden upstream package `config`.
<!-- featureliftbench:behavior-clauses:end -->
