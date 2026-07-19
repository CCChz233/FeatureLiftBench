# FeatureLift Task: Schema load and dump

Extract Marshmallow Schema declaration, field validation, nested schemas, and load/dump round-trips.

## Target API

- Import: `from featurelifted import Schema, fields, ValidationError, EXCLUDE, RAISE; from featurelifted.decorators import post_load, validates_schema`
- Callable: `featurelifted.Schema.load`
- Signature: `Schema.load(data, *, many: bool = False, partial=None, unknown=RAISE)`

## Excluded Behavior

- flask-smorest and web framework integrations
- original project tests and packaging metadata
- schema class registry across entry points

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `marshmallow`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — declare Schema subclasses with typed fields
- **B002** — load dict payloads with validation and nested schemas
- **B003** — dump objects to dicts with field selection
- **B004** — handle unknown=EXCLUDE and partial load validation errors
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: marshmallow
<!-- featureliftbench:behavior-clauses:end -->
