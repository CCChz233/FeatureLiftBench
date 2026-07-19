# FeatureLift Task: Layered settings merge

Extract Dynaconf object_merge and LazySettings layered TOML/env merge without importing dynaconf.

## Target API

- Import: `from featurelifted import Dynaconf, object_merge; from featurelifted.utils import object_merge as merge_util`
- Callable: `featurelifted.utils.object_merge`
- Signature: `object_merge(old, new, unique=False, full_path=None, list_merge='merge')`

## Excluded Behavior

- Flask/Django extensions and CLI
- vault/redis external loaders
- typed settings subsystem and validators beyond merge
- original dynaconf import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `dynaconf`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — recursive object_merge with list_merge shallow/deep/merge modes
- **B002** — Dynaconf loads layered TOML settings files with environment sections
- **B003** — envvar_prefix overrides nested keys with precedence over file values
- **B004** — merge_enabled combines multiple settings files
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: dynaconf
<!-- featureliftbench:behavior-clauses:end -->
