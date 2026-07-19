# FeatureLift Task: YAML config bootstrap

Extract layered YAML config loading, env expansion, and deep merge bootstrap used by VibeShop.

## Target API

- Import: `from featurelifted import bootstrap_config, merge_config_layers; from featurelifted.config_loader import load_yaml_config; from featurelifted.state import GLOBAL_STATE, reset_state`
- Callable: `featurelifted.bootstrap_config`
- Signature: `bootstrap_config(config_dir: str | Path) -> dict`

## Excluded Behavior

- pricing computation and CSV transforms
- HTTP routes and app factory
- broken bootstrap_config_fast shortcut
- legacy shallow merge helper for production use
- original project tests and CLI entrypoints

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `vibe_app`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — deep-merge layered config dicts with later overrides
- **B002** — bootstrap default/app/pricing/tiers YAML layers from a directory
- **B003** — expand ${ENV:-default} placeholders while loading YAML
- **B004** — record bootstrap side effects in process registry state
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: vibe_app
<!-- featureliftbench:behavior-clauses:end -->
