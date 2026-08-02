# FeatureLift Task: Version parse/compare/bump

Extract a task-scoped subset of `semver` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    Version,
)
```

## Required API Details

- `Version(major: int, minor: int = 0, patch: int = 0, prerelease: str | None = None, build: str | None = None)` class constructor
  - `Version.parse(version: str) -> Version`
  - `Version.compare(self, other: Version) -> int`
  - `Version.bump_major(self) -> Version`
  - `Version.bump_minor(self) -> Version`
  - `Version.bump_patch(self) -> Version`
  - `Version.replace(self, **parts) -> Version`
  - `Version.major` attribute must exist on instances
  - `Version.minor` attribute must exist on instances
  - `Version.patch` attribute must exist on instances
  - `Version.prerelease` attribute must exist on instances
  - `Version.build` attribute must exist on instances

## Required Behavior

- The extracted feature must support this observable behavior: parse semver strings into Version. Required observable cases include parse basic; prerelease and build parse.
- The extracted feature must support this observable behavior: compare and order Version instances. Required observable cases include compare and order; ordering operators.
- The extracted feature must support this observable behavior: bump major/minor/patch and replace parts. Required observable cases include bump and replace; constructor defaults.
- Invalid version strings raise ValueError.
- The package exposes the required task API paths `featurelifted.Version`, `featurelifted.Version.parse`, `featurelifted.Version.compare`, `featurelifted.Version.bump_major`, `featurelifted.Version.bump_minor`, `featurelifted.Version.bump_patch`, `featurelifted.Version.replace` with the kinds and callable signatures listed in this contract.
- the submitted package does not import forbidden upstream packages: semver.

## Constraints

- Forbidden imports: `semver`.
- Do not implement CLI entry points.
- Do not implement file reading helpers.
- Do not implement deprecated VersionInfo-only quirks beyond optional alias.
- Do not implement original semver import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: parse semver strings into Version. Required observable cases include parse basic; prerelease and build parse.
- **B002** — The extracted feature must support this observable behavior: compare and order Version instances. Required observable cases include compare and order; ordering operators.
- **B003** — The extracted feature must support this observable behavior: bump major/minor/patch and replace parts. Required observable cases include bump and replace; constructor defaults.
- **B004** — Invalid version strings raise ValueError.
- **B005** — The package exposes the required task API paths `featurelifted.Version`, `featurelifted.Version.parse`, `featurelifted.Version.compare`, `featurelifted.Version.bump_major`, `featurelifted.Version.bump_minor`, `featurelifted.Version.bump_patch`, `featurelifted.Version.replace` with the kinds and callable signatures listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: semver.
<!-- featureliftbench:behavior-clauses:end -->
