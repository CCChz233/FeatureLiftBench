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

- `OmegaConf.create` callable must exist
- `OmegaConf.merge` callable must exist
- `OmegaConf.to_container` callable must exist
- `OmegaConf.select` callable must exist
- `OmegaConf.resolve` callable must exist
- `OmegaConf.is_missing` callable must exist
- `OmegaConf.is_config` callable must exist
- `OmegaConf.set_struct` callable must exist
- `errors.InterpolationResolutionError` must be importable and raisable
- `errors.ConfigKeyError` must be importable and raisable

## Required Behavior

- The extracted feature must support this observable behavior: create/merge/to_container with interpolation resolve and select. Required observable cases include create merge resolve; select.
- The extracted feature must support this observable behavior: is_missing/is_config helpers and resolve inplace. Required observable cases include is helpers; resolve inplace.
- The extracted feature must support this observable behavior: InterpolationResolutionError and struct-mode key errors. Required observable cases include interpolation error; struct mode key error.
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

- **B001** — The extracted feature must support this observable behavior: create/merge/to_container with interpolation resolve and select. Required observable cases include create merge resolve; select.
- **B002** — The extracted feature must support this observable behavior: is_missing/is_config helpers and resolve inplace. Required observable cases include is helpers; resolve inplace.
- **B003** — The extracted feature must support this observable behavior: InterpolationResolutionError and struct-mode key errors. Required observable cases include interpolation error; struct mode key error.
- **B004** — ListConfig merge replaces list values as upstream default merge semantics used in tests.
- **B005** — The package exposes the required OmegaConf methods and InterpolationResolutionError/ConfigKeyError with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: omegaconf.
<!-- featureliftbench:behavior-clauses:end -->
