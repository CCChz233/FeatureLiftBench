# FeatureLift Task: User/cache/config/data path resolver

Extract a small, deterministic subset of `platformdirs` path resolution into a standalone `featurelifted` package.

The implementation must not import `platformdirs`, must not read from `repo/`, must not use the network, and must not depend on external services. Use only the standard library.

## Target API

```python
from featurelifted import user_cache_dir, user_config_dir, user_data_dir

user_data_dir(appname=None, appauthor=None, version=None, roaming=False, platform="linux", env=None, home=None) -> str
user_config_dir(appname=None, appauthor=None, version=None, roaming=False, platform="linux", env=None, home=None) -> str
user_cache_dir(appname=None, appauthor=None, version=None, opinion=True, platform="linux", env=None, home=None) -> str
```

`env` is an optional mapping of environment variable names to values. If omitted, the function may read `os.environ`.
`home` is an optional explicit home directory used by the tests to avoid depending on the host machine.
`platform` accepts Linux-like values, macOS-like values (`darwin`, `macos`), and Windows-like values (`win32`, `windows`).

## Required Behavior

- Linux:
  - `XDG_DATA_HOME`, `XDG_CONFIG_HOME`, and `XDG_CACHE_HOME` override defaults when they are non-blank.
  - Defaults are `~/.local/share`, `~/.config`, and `~/.cache`.
  - Append `appname` and then `version` when provided.
- macOS:
  - Data and config default to `~/Library/Application Support`.
  - Cache defaults to `~/Library/Caches`.
  - XDG overrides still take precedence when non-blank.
- Windows:
  - Data/config use `LOCALAPPDATA` by default and `APPDATA` when `roaming=True`.
  - Cache uses `LOCALAPPDATA`.
  - When `appauthor` is `None`, use `appname` as the author segment.
  - When `appauthor` is `False`, omit the author segment.
  - Cache inserts `Cache` before `version` when `opinion=True`.

## Constraints

- Forbidden imports: `platformdirs`.
- Forbidden path access: `repo/`, `src/platformdirs/`.
- Do not create directories on disk.
- Do not implement unrelated media, site, Android, or CLI helpers.

## Public vs Hidden Tests

Public tests cover Linux defaults, Linux XDG overrides, and basic Windows roaming/cache layout.
Hidden tests cover macOS defaults and XDG precedence, blank XDG fallback, Windows `appauthor=False`, Windows `opinion=False`, and no-appname base directory behavior.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — Linux XDG_DATA_HOME, XDG_CONFIG_HOME, and XDG_CACHE_HOME precedence
- **B002** — Linux default ~/.local/share, ~/.config, and ~/.cache fallbacks
- **B003** — macOS Application Support and Caches defaults
- **B004** — macOS XDG override precedence
- **B005** — Windows LocalAppData vs AppData roaming behavior
- **B006** — Windows appauthor, appauthor=False, version, and cache opinion semantics
- **B007** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B008** — the submitted package does not import forbidden upstream packages: platformdirs
<!-- featureliftbench:behavior-clauses:end -->
