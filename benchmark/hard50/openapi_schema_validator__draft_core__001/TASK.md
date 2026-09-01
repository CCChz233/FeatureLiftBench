# FeatureLift Task: OpenAPI dialect JSON Schema validation

Build a standalone `featurelifted` package that validates instances against in-memory OpenAPI 3.0 schema dicts, including nullable and discriminator mapping.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    OAS30Validator,
    validate,
)
```

## Required API Details

- `validate(instance, schema, cls=..., *args, allow_remote_references=False, check_schema=True, enforce_properties_required=False, **kwargs)`
- `OAS30Validator` class must be importable

## Required Behavior

- `validate` accepts a Python schema dict (not a URL) and an instance that matches an OAS 3.0 string schema, including `nullable: true` which allows `None`.
- With `cls=OAS30Validator`, an instance whose type is not allowed by the schema raises `jsonschema.exceptions.ValidationError`.
- An OAS 3.0 `oneOf` schema with a `discriminator.propertyName` and local `#/components/schemas/...` mapping validates the matching variant from an in-memory schema dict.
- A discriminator-selected variant that is missing a required property raises `jsonschema.exceptions.ValidationError`.
- The package exposes `validate` and `OAS30Validator` with the callable paths listed in this contract.
- The submitted package source does not import the forbidden upstream package `openapi_schema_validator`.

## Constraints

- Forbidden imports: `openapi_schema_validator`.
- Do not implement full OpenAPI document walk.
- Do not implement remote $ref retrieval / urllib.
- Do not implement runtime import of openapi_schema_validator.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — `validate` accepts a Python schema dict (not a URL) and an instance that matches an OAS 3.0 string schema, including `nullable: true` which allows `None`.
- **B002** — With `cls=OAS30Validator`, an instance whose type is not allowed by the schema raises `jsonschema.exceptions.ValidationError`.
- **B003** — An OAS 3.0 `oneOf` schema with a `discriminator.propertyName` and local `#/components/schemas/...` mapping validates the matching variant from an in-memory schema dict.
- **B004** — A discriminator-selected variant that is missing a required property raises `jsonschema.exceptions.ValidationError`.
- **B005** — The package exposes `validate` and `OAS30Validator` with the callable paths listed in this contract.
- **B006** — The submitted package source does not import the forbidden upstream package `openapi_schema_validator`.
<!-- featureliftbench:behavior-clauses:end -->
