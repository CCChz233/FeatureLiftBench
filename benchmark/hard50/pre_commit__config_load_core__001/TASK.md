# FeatureLift Task: YAML config load and normalize

Build a standalone `featurelifted` package that loads and normalizes a pre-commit YAML config file without cloning repositories or installing languages.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    InvalidConfigError,
    load_config,
)
```

## Required API Details

- `load_config(filename: str) -> dict`
- `InvalidConfigError` must be importable and raisable

## Required Behavior

- Loading a local-repo YAML config returns a dict whose first hook keeps the declared `id`, `language`, and `entry`, and fills `language_version` with `'default'` and `pass_filenames` with True when those keys are omitted.
- Loading a config whose only content is `repos: []` yields `minimum_pre_commit_version` equal to `'0'`.
- Loading YAML that does not match the config schema, including a local hook whose `entry` is not a string, raises `InvalidConfigError`.
- A local hook whose language is `system` is normalized so that the loaded hook `language` is `unsupported`.
- The package exposes `load_config` and `InvalidConfigError` with the callable signatures listed in this contract.
- The submitted package source does not import the forbidden upstream package `pre_commit`.

## Constraints

- Forbidden imports: `pre_commit`.
- Do not implement git clone of repos.
- Do not implement language environment install.
- Do not implement hook execution.
- Do not implement runtime import of pre_commit.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — Loading a local-repo YAML config returns a dict whose first hook keeps the declared `id`, `language`, and `entry`, and fills `language_version` with `'default'` and `pass_filenames` with True when those keys are omitted.
- **B002** — Loading a config whose only content is `repos: []` yields `minimum_pre_commit_version` equal to `'0'`.
- **B003** — Loading YAML that does not match the config schema, including a local hook whose `entry` is not a string, raises `InvalidConfigError`.
- **B004** — A local hook whose language is `system` is normalized so that the loaded hook `language` is `unsupported`.
- **B005** — The package exposes `load_config` and `InvalidConfigError` with the callable signatures listed in this contract.
- **B006** — The submitted package source does not import the forbidden upstream package `pre_commit`.
<!-- featureliftbench:behavior-clauses:end -->
