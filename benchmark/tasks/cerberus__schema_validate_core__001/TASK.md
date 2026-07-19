# FeatureLift Task: Schema validation core

Extract Cerberus Validator with nested schema rules, type coercion, and structured error aggregation without original cerberus import.

## Target API

- Import: `import featurelifted; from featurelifted import Validator, DocumentError, SchemaError`
- Callable: `featurelifted.Validator`
- Signature: `Validator(schema=None, allow_unknown=False, require_all=False)(document)`

## Excluded Behavior

- schema_registry and rules_set_registry named schema indirection
- normalization rename/default pipelines beyond coerce in tests
- benchmarks, upstream tests, docs, and packaging metadata
- original cerberus import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `cerberus`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — validate dict documents against nested schema definitions
- **B002** — enforce required fields and type rules on nested mappings and lists
- **B003** — coerce field values during validation and reflect coerced document
- **B004** — aggregate nested validation failures into structured error trees
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: cerberus
<!-- featureliftbench:behavior-clauses:end -->
