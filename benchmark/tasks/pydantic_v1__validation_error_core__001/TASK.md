# FeatureLift Task: BaseModel validation and structured ValidationError core

Extract Pydantic v1 BaseModel field parsing, validator/root_validator hooks, model Config, and ValidationError error trees without JSON Schema, networks, or settings machinery.

## Target API

- Import: `import featurelifted; from featurelifted import BaseModel, Field, ValidationError, validator, root_validator, Extra`
- Callable: `featurelifted.BaseModel.parse_obj`
- Signature: `BaseModel.parse_obj(obj)`

## Excluded Behavior

- JSON Schema generation and schema_json
- network/email/DSN types and BaseSettings
- dataclasses bridge, validate_arguments, mypy plugin
- original pydantic package import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `pydantic`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — declare BaseModel subclasses and parse dict input
- **B002** — field validators with pre/each_item semantics
- **B003** — root_validator whole-model checks
- **B004** — Config.extra forbid for unknown keys
- **B005** — ValidationError.errors() with loc/type/msg for nested models
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: pydantic
<!-- featureliftbench:behavior-clauses:end -->
