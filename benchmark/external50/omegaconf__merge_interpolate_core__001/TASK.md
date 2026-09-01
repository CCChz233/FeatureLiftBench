# FeatureLift Task: omegaconf merge interpolate

Extract a task-scoped subset of `omegaconf` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    errors,
    OmegaConf,
)
```

## Required API Details

- `OmegaConf.create(obj=None)`
- `OmegaConf.merge(*configs)`
- `OmegaConf.to_container(cfg, *, resolve=False)`
- `OmegaConf.select(cfg, key, default=None)`
- `OmegaConf.resolve(cfg) -> None`
- `OmegaConf.is_missing(cfg, key) -> bool`
- `OmegaConf.is_config(obj) -> bool`
- `OmegaConf.set_struct(cfg, flag: bool) -> None`
- `errors.InterpolationResolutionError` must be importable and raisable
- `errors.ConfigKeyError` must be importable and raisable

## Required Behavior

- OmegaConf.create builds attribute-accessible configuration trees; OmegaConf.merge combines mappings, OmegaConf.to_container(..., resolve=True) replaces ${key} interpolations with their values, and OmegaConf.select resolves dotted paths while returning its default for a missing path.
- `OmegaConf.is_missing` and `OmegaConf.is_config` classify missing and config nodes; after `OmegaConf.resolve(cfg)`, interpolated values are readable by attribute access on the resolved tree.
- Resolving a missing interpolation with OmegaConf.to_container(..., resolve=True) raises InterpolationResolutionError, and assigning an unknown key after OmegaConf.set_struct(cfg, True) raises a key-related exception such as ConfigKeyError.
- ListConfig merge replaces list values as upstream default merge semantics used in tests.
- The package exposes the required OmegaConf methods and InterpolationResolutionError/ConfigKeyError with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: omegaconf.

## Constraints

- Forbidden imports: `omegaconf`.
- Do not implement dataclass structured configs.
- Do not implement custom resolver registration.
- Do not implement original omegaconf import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — OmegaConf.create builds attribute-accessible configuration trees; OmegaConf.merge combines mappings, OmegaConf.to_container(..., resolve=True) replaces ${key} interpolations with their values, and OmegaConf.select resolves dotted paths while returning its default for a missing path.
- **B002** — `OmegaConf.is_missing` and `OmegaConf.is_config` classify missing and config nodes; after `OmegaConf.resolve(cfg)`, interpolated values are readable by attribute access on the resolved tree.
- **B003** — Resolving a missing interpolation with OmegaConf.to_container(..., resolve=True) raises InterpolationResolutionError, and assigning an unknown key after OmegaConf.set_struct(cfg, True) raises a key-related exception such as ConfigKeyError.
- **B004** — ListConfig merge replaces list values as upstream default merge semantics used in tests.
- **B005** — The package exposes the required OmegaConf methods and InterpolationResolutionError/ConfigKeyError with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: omegaconf.
<!-- featureliftbench:behavior-clauses:end -->
