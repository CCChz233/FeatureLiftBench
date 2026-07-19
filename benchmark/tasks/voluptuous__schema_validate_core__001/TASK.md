# FeatureLift Task: Schema validation core

Extract Voluptuous Schema declaration, Required/Optional markers, composed validators, and error aggregation without original voluptuous import.

## Target API

- Import: `import featurelifted; from featurelifted import Schema, Required, Optional, All, Any, In, Coerce, Invalid, MultipleInvalid, SchemaError`
- Callable: `featurelifted.Schema`
- Signature: `Schema(schema, required=False, extra=PREVENT_EXTRA)(data)`

## Excluded Behavior

- humanize_error and CLI helpers
- Email, Url, File, and other heavyweight validators
- original voluptuous import at runtime
- upstream packaging and bin scripts

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `voluptuous`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — declare Schema with Required and Optional markers
- **B002** — validate dict payloads with type and nested schema matching
- **B003** — compose All, Any, and In validators with Coerce
- **B004** — aggregate validation failures as MultipleInvalid with error paths
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: voluptuous
<!-- featureliftbench:behavior-clauses:end -->
