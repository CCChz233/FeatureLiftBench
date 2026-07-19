# FeatureLift Task: Dataclass JSON serde core

Extract dataclass to/from JSON with field config, letter-case transforms, and exclusion predicates without original dataclasses_json import.

## Target API

- Import: `import featurelifted; from featurelifted import DataClassJsonMixin, LetterCase, Exclude, Undefined, dataclass_json, config, global_config; from featurelifted.undefined import UndefinedParameterError`
- Callable: `featurelifted.dataclass_json`
- Signature: `dataclass_json(cls=None, *, letter_case=None, undefined=None)`

## Excluded Behavior

- marshmallow schema generation and mm_field validation
- CatchAll undefined INCLUDE mode and schema dump hooks
- upstream tests, docs, CI, and packaging metadata
- original dataclasses_json import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `dataclasses_json`, `dataclasses-json`, `marshmallow`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — round-trip dataclass instances through JSON and dict payloads
- **B002** — apply class-level and field-level letter case transforms
- **B003** — exclude fields via config predicates and Exclude helpers
- **B004** — register per-type encoders and decoders via config and global_config
- **B005** — decode nested dataclass fields recursively
- **B006** — reject unknown keys when undefined=Undefined.RAISE
- **B007** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B008** — the submitted package does not import forbidden upstream packages: dataclasses_json, dataclasses-json, marshmallow
<!-- featureliftbench:behavior-clauses:end -->
