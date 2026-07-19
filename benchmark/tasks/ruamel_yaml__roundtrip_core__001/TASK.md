# FeatureLift Task: YAML roundtrip with comments

Extract ruamel.yaml round-trip load/dump preserving comments and key order.

## Target API

- Import: `import featurelifted; from featurelifted import YAML, round_trip_load, round_trip_dump, CommentedMap`
- Callable: `featurelifted.round_trip_load`
- Signature: `round_trip_load(stream) -> CommentedMap`

## Excluded Behavior

- C yaml acceleration
- jinja2 templating
- original ruamel import

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `ruamel`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — round-trip load/dump preserves end-of-line comments
- **B002** — CommentedMap key order preserved
- **B003** — flow style and literal block scalars
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: ruamel
<!-- featureliftbench:behavior-clauses:end -->
