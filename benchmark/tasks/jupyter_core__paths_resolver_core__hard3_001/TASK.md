# FeatureLift Task: Jupyter Config/Data/Runtime Path Resolution

Extract the selected path-resolution behavior from `jupyter_core` into a
standalone Python package named `featurelifted`.

## Target API

- `jupyter_config_dir(env=None, home=None, platform="linux") -> str`
- `jupyter_data_dir(env=None, home=None, platform="linux") -> str`
- `jupyter_runtime_dir(env=None, home=None, platform="linux") -> str`
- `jupyter_path(*subdirs, env=None, home=None, platform="linux", sys_prefix="/usr", user_site_base=None, enable_user_site=True) -> list[str]`
- `jupyter_config_path(env=None, home=None, platform="linux", sys_prefix="/usr", user_site_base=None, enable_user_site=True) -> list[str]`

## Feature Specification

Preserve Jupyter path precedence for config, data, and runtime paths:

- explicit `JUPYTER_CONFIG_PATH` and `JUPYTER_PATH` entries are highest priority;
- `JUPYTER_CONFIG_DIR`, `JUPYTER_DATA_DIR`, and `JUPYTER_RUNTIME_DIR` override user defaults;
- Linux, macOS, and Windows have distinct default data path behavior;
- `JUPYTER_NO_CONFIG` returns an isolated clean config dir and suppresses broader config search;
- `JUPYTER_PREFER_ENV_PATH` moves environment-level paths before user-level paths;
- requested `jupyter_path("kernels")` subdirectories are appended to each search root.

The API accepts explicit `env`, `home`, and `platform` inputs so tests do not
depend on the host machine.

## Constraints

- Do not import `jupyter_core` or `platformdirs`.
- Do not read from `repo/` or any original source snapshot path at runtime.
- Do not use network, databases, Redis, browsers, remote APIs, or host-specific home directories.
- Keep the extraction focused on path resolution; do not copy CLI, migration, application, or troubleshooting modules.

## Public vs Hidden Test Intent

Public tests cover basic path precedence and platform defaults. Hidden tests
cover disabled config behavior, runtime fallback, environment-over-user order,
Windows path separators, and system-path exclusion.
