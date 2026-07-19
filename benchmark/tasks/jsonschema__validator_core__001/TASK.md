# FeatureLift Task: JSON Schema Draft 2020-12 validation core

Extract jsonschema's core Draft 2020-12 validation behavior for common schema constraints and structured errors.

## Target API

- Import: `from featurelifted import Draft202012Validator, validate, ValidationError, SchemaError, FormatChecker`
- Callable: `featurelifted.Draft202012Validator`
- Signature: `Draft202012Validator(schema, resolver=None, format_checker=None)`

## Excluded Behavior

- remote reference retrieval over network
- CLI tooling
- benchmark suites and documentation

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `jsonschema`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — validate object, array, string, integer, number, boolean, and null types
- **B002** — support required, properties, additionalProperties, minimum, minLength, pattern, enum, anyOf, oneOf, and allOf
- **B003** — iterate ValidationError objects with path, schema_path, validator, validator_value, and message
- **B004** — perform format validation when a FormatChecker is provided
- **B005** — validate schemas and raise SchemaError for invalid schemas
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: jsonschema
<!-- featureliftbench:behavior-clauses:end -->
