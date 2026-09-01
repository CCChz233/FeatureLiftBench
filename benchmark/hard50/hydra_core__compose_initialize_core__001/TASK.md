# FeatureLift Task: Hydra compose and initialize core

Extract deterministic local YAML initialization and composition into a standalone `featurelifted` package while preserving the required global lifecycle.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    compose,
    GlobalHydra,
    initialize,
)
```

## Required API Details

- `initialize(config_path: str | None = None, job_name: str | None = None, caller_stack_depth: int = 1, version_base: str | None = <unspecified>)` class constructor
  - `initialize.__enter__(self, *args, **kwargs) -> None`
  - `initialize.__exit__(self, exc_type, exc_val, exc_tb) -> None`
- `compose(config_name: str | None = None, overrides: list[str] | None = None, return_hydra_config: bool = False) -> omegaconf.DictConfig`
- `GlobalHydra()` class constructor
  - `GlobalHydra.instance(*args, **kwargs) -> GlobalHydra`
  - `GlobalHydra.is_initialized(self) -> bool`
  - `GlobalHydra.clear(self) -> None`

## Required Behavior

- Calling `initialize` with a relative configuration directory marks `GlobalHydra.instance()` initialized; using it as a context manager permits `compose` calls inside the context and restores the prior global initialization state on exit. An absolute `config_path` is rejected.
- Given a caller-relative directory containing YAML files, `compose(config_name)` loads the named `.yaml` configuration as an `omegaconf.DictConfig`; a YAML `defaults` list selects configuration-group files and merges their values into the declared package while `_self_` preserves primary-config values.
- When composing a YAML configuration, override strings can select a different group with `group=choice`, replace existing nested scalar values with dotted keys such as `service.port=9000`, and add missing dotted values with a leading `+`; YAML scalar types are preserved.
- `GlobalHydra.instance()` is a process-global singleton; `is_initialized()` reports lifecycle state, `clear()` resets it, composing before initialization fails, and initialization can succeed again after clearing.
- The package exposes `initialize`, `compose`, and `GlobalHydra` with the required members, kinds, and callable signatures listed in this contract.

## Constraints

- Forbidden imports: `hydra`.
- Do not implement remote launchers, remote configuration sources, and sweepers.
- Do not implement job execution, multirun, logging setup, and working-directory changes.
- Do not implement plugin discovery and structured ConfigStore registration.
- Do not implement the original hydra package at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — Calling `initialize` with a relative configuration directory marks `GlobalHydra.instance()` initialized; using it as a context manager permits `compose` calls inside the context and restores the prior global initialization state on exit. An absolute `config_path` is rejected.
- **B002** — Given a caller-relative directory containing YAML files, `compose(config_name)` loads the named `.yaml` configuration as an `omegaconf.DictConfig`; a YAML `defaults` list selects configuration-group files and merges their values into the declared package while `_self_` preserves primary-config values.
- **B003** — When composing a YAML configuration, override strings can select a different group with `group=choice`, replace existing nested scalar values with dotted keys such as `service.port=9000`, and add missing dotted values with a leading `+`; YAML scalar types are preserved.
- **B004** — `GlobalHydra.instance()` is a process-global singleton; `is_initialized()` reports lifecycle state, `clear()` resets it, composing before initialization fails, and initialization can succeed again after clearing.
- **B005** — The package exposes `initialize`, `compose`, and `GlobalHydra` with the required members, kinds, and callable signatures listed in this contract.
<!-- featureliftbench:behavior-clauses:end -->
