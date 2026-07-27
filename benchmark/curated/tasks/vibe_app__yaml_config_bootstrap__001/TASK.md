# FeatureLift Task: YAML config bootstrap

Extract a task-scoped subset of `vibe_app` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    bootstrap_config,
    config_loader,
    merge_config_layers,
    state,
)
```

## Required API Details

- `bootstrap_config(config_dir: 'str | Path') -> 'dict[str, Any]'`
- `merge_config_layers(*layers: 'dict[str, Any]') -> 'dict[str, Any]'`
- `config_loader` module must be importable
  - `config_loader.load_yaml_config(path: 'str | Path') -> 'dict[str, Any]'`
- `state` module must be importable
  - `state.GLOBAL_STATE` constant must exist
  - `state.reset_state() -> 'None'`

## Required Behavior

- The extracted feature must support this observable behavior: deep-merge layered config dicts with later overrides. Required observable cases include merge config layers deep merges nested keys; bootstrap config loads repo layers; merge does not mutate inputs.
- The extracted feature must support this observable behavior: bootstrap default/app/pricing/tiers YAML layers from a directory. Required observable cases include bootstrap config loads repo layers; merge does not mutate inputs.
- The extracted feature must support this observable behavior: expand ${ENV:-default} placeholders while loading YAML. Required observable cases include env placeholder expansion.
- The extracted feature must support this observable behavior: record bootstrap side effects in process registry state. Required observable cases include bootstrap records side effects.
- The package exposes the required task API paths `featurelifted.bootstrap_config`, `featurelifted.merge_config_layers`, `featurelifted.config_loader`, `featurelifted.config_loader.load_yaml_config`, `featurelifted.state`, `featurelifted.state.GLOBAL_STATE`, `featurelifted.state.reset_state` with the kinds and callable signatures listed in this contract.

## Constraints

- Forbidden imports: `vibe_app`.
- Do not implement pricing computation and CSV transforms.
- Do not implement HTTP routes and app factory.
- Do not implement broken bootstrap_config_fast shortcut.
- Do not implement legacy shallow merge helper for production use.
- Do not implement original project tests and CLI entrypoints.

## Public vs Hidden Tests

Benchmark evaluator tests remain private. Each evaluator test maps to the public behaviors above and only deepens examples, boundaries, or combinations within those declared behaviors.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: deep-merge layered config dicts with later overrides. Required observable cases include merge config layers deep merges nested keys; bootstrap config loads repo layers; merge does not mutate inputs.
- **B002** — The extracted feature must support this observable behavior: bootstrap default/app/pricing/tiers YAML layers from a directory. Required observable cases include bootstrap config loads repo layers; merge does not mutate inputs.
- **B003** — The extracted feature must support this observable behavior: expand ${ENV:-default} placeholders while loading YAML. Required observable cases include env placeholder expansion.
- **B004** — The extracted feature must support this observable behavior: record bootstrap side effects in process registry state. Required observable cases include bootstrap records side effects.
- **B005** — The package exposes the required task API paths `featurelifted.bootstrap_config`, `featurelifted.merge_config_layers`, `featurelifted.config_loader`, `featurelifted.config_loader.load_yaml_config`, `featurelifted.state`, `featurelifted.state.GLOBAL_STATE`, `featurelifted.state.reset_state` with the kinds and callable signatures listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: vibe_app.
<!-- featureliftbench:behavior-clauses:end -->
