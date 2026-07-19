# FeatureLift Task: attrs field validators

Extract attrs class definition with field validators and validate() as a standalone package.

## Target API

- Import: `from featurelifted import define, field, validate; from featurelifted import validators`
- Callable: `featurelifted.validators.instance_of`
- Signature: `instance_of(type: type) -> Callable`

## Excluded Behavior

- cmp, converters beyond validator helpers, and custom setters
- asdict, astuple, and serialization helpers
- original project tests and documentation

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `attrs`, `attr`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — attach validators to fields on define() classes
- **B002** — run instance_of, ge, lt, matches_re, in_, and length validators
- **B003** — compose validators with and_, not_, and optional
- **B004** — validate deep_iterable and deep_mapping structures
- **B005** — globally disable validators with set_disabled and validate()
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: attrs, attr
<!-- featureliftbench:behavior-clauses:end -->
