# FeatureLift Task: ConfigBox dot-access config transforms

Extract python-box ConfigBox typed accessors without importing box.

## Target API

- Import: `import featurelifted; from featurelifted import Box, ConfigBox; from featurelifted.exceptions import BoxKeyError`
- Callable: `featurelifted.ConfigBox`
- Signature: `ConfigBox(*args, **kwargs) -> ConfigBox`

## Excluded Behavior

- yaml/toml/msgpack converters and file loaders
- ShorthandBox and BoxList extras
- original box import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `box`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — dot and bracket dict access
- **B002** — case-insensitive ConfigBox keys
- **B003** — bool/int/float/list coercion helpers
- **B004** — default values on missing keys
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: box
<!-- featureliftbench:behavior-clauses:end -->
