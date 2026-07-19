# FeatureLift Task: Hook specification, registration, and call ordering

Extract pluggy's core plugin manager behavior for declaring hooks, registering implementations, and dispatching calls.

## Target API

- Import: `from featurelifted import PluginManager, HookspecMarker, HookimplMarker, PluginValidationError`
- Callable: `featurelifted.PluginManager`
- Signature: `PluginManager(project_name: str)`

## Excluded Behavior

- pytest integration
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

- **B001** — declare hook specifications with HookspecMarker
- **B002** — register plugins and call hook implementations through PluginManager
- **B003** — respect tryfirst and trylast ordering
- **B004** — support firstresult hooks
- **B005** — support hookwrapper implementations that inspect or modify results
- **B006** — reject unknown hook implementation arguments during validation
- **B007** — support unregistering plugins and querying registered plugin names
- **B008** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B009** — the submitted package does not import forbidden upstream packages: pluggy
<!-- featureliftbench:behavior-clauses:end -->
