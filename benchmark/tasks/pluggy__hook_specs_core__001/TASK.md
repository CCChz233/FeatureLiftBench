# FeatureLift Task: Hook specification validation and discovery

Extract pluggy hook specification declaration, validation, and pending-hook checks as a standalone package.

## Target API

- Import: `from featurelifted import PluginManager, HookspecMarker, HookimplMarker, PluginValidationError`
- Callable: `featurelifted.PluginManager.check_pending`
- Signature: `PluginManager.check_pending() -> None`

## Excluded Behavior

- pytest integration and setuptools entry point loading
- project packaging metadata
- development tests and release tooling

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `pluggy`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — declare hook specifications with HookspecMarker including firstresult and historic flags
- **B002** — reject hook implementations with unknown arguments during registration
- **B003** — reject hookwrapper implementations that are not generator functions
- **B004** — reject historic hookwrapper combinations via PluginValidationError
- **B005** — check_pending raises for unknown non-optional hook implementations
- **B006** — support optionalhook implementations for undeclared hooks
- **B007** — replay historic hook calls for plugins registered after the first dispatch
- **B008** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B009** — the submitted package does not import forbidden upstream packages: pluggy
<!-- featureliftbench:behavior-clauses:end -->
