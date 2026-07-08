# FeatureLift Task: Settings/profile resolution and skip matching

Extract a task-scoped subset of `isort` settings resolution into a standalone `featurelifted` package.

The implementation must not import `isort`, must not read from `repo/`, must not use the network, and must not depend on external services. Use only the standard library.

## Target API

```python
from featurelifted import (
    ProfileDoesNotExist,
    Settings,
    UnsupportedSettings,
    find_config,
    resolve_from_path,
    resolve_settings,
    should_skip,
)
```

Required behavior:

- `resolve_settings(config_files=(), profile=None, overrides=None) -> Settings`
- `resolve_from_path(start_path, profile=None, overrides=None) -> Settings`
- `find_config(start_path) -> Path | None`
- `should_skip(path, settings) -> bool`
- `Settings.is_skipped(path) -> bool`

## Required Behavior

- Support at least the `black`, `django`, and `google` profiles.
- Merge settings in this order: defaults, selected profile, config files, runtime overrides.
- Parse `pyproject.toml`, `setup.cfg`, `tox.ini`, `.isort.cfg`, and `.editorconfig` sections used by isort.
- Resolve `src_paths` relative to the config file directory.
- Merge `skip` with `extend_skip`.
- Merge `skip_glob` with `extend_skip_glob`.
- Skip paths matching explicit skip names or glob patterns.
- Existing files with no matching skip rule must not be skipped.
- Unknown profiles must raise `ProfileDoesNotExist`.
- Unsupported options must raise `UnsupportedSettings`.

## Constraints

- Forbidden imports: `isort`.
- Forbidden path access: `repo/`, `isort/`.
- Do not implement import sorting, parser/formatter internals, CLI behavior, git integration, or entry point plugins.

## Public vs Hidden Tests

Public tests cover profile + pyproject merging, runtime override precedence, skip names, and config discovery from a path.
Hidden tests cover extend skip globs, existing-file non-skip behavior, src path resolution, config-file precedence, invalid profile, unsupported setting, and `.editorconfig` line length mapping.
