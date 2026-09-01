# FeatureLift Task: Config and plugin id filters

Build a standalone `featurelifted` package that loads Bandit YAML configuration and filters plugin test ids by include/exclude sets.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    BanditConfig,
    BanditTestSet,
    ConfigError,
)
```

## Required API Details

- `BanditConfig(config_file=None)` class constructor
  - `BanditConfig.__init__(self, config_file=None)`
  - `BanditConfig.get_option(self, option_string)`
- `BanditTestSet(config, profile=None)` class constructor
  - `BanditTestSet.__init__(self, config, profile=None)`
  - `BanditTestSet.get_tests(self, checktype)`
  - `BanditTestSet._get_filter(config, profile)`
- `ConfigError` must be importable and raisable

## Required Behavior

- Constructing `BanditConfig` with a YAML file that lists `skips` and `tests` makes those lists available through `get_option('skips')` and `get_option('tests')`.
- When a profile `include` list is supplied, `BanditTestSet._get_filter` returns exactly those test ids.
- When a profile lists both `include` and `exclude` ids, `_get_filter` returns the include set minus the exclude set.
- Constructing `BanditConfig` with invalid YAML or a missing file raises `ConfigError`.
- The package exposes `BanditConfig`, `BanditTestSet`, and `ConfigError` with the callable signatures listed in this contract.
- The submitted package source does not import the forbidden upstream package `bandit`.

## Constraints

- Forbidden imports: `bandit`.
- Do not implement full repository scan CLI.
- Do not implement SARIF/HTML formatters.
- Do not implement live plugin marketplace.
- Do not implement runtime import of bandit.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — Constructing `BanditConfig` with a YAML file that lists `skips` and `tests` makes those lists available through `get_option('skips')` and `get_option('tests')`.
- **B002** — When a profile `include` list is supplied, `BanditTestSet._get_filter` returns exactly those test ids.
- **B003** — When a profile lists both `include` and `exclude` ids, `_get_filter` returns the include set minus the exclude set.
- **B004** — Constructing `BanditConfig` with invalid YAML or a missing file raises `ConfigError`.
- **B005** — The package exposes `BanditConfig`, `BanditTestSet`, and `ConfigError` with the callable signatures listed in this contract.
- **B006** — The submitted package source does not import the forbidden upstream package `bandit`.
<!-- featureliftbench:behavior-clauses:end -->
