from __future__ import annotations

import pytest
from jsonschema.exceptions import ValidationError
from featurelifted import OAS30Validator, validate

PET_SCHEMA = {
        "$ref": "#/components/schemas/Pet",
        "components": {
            "schemas": {
                "Cat": {
                    "type": "object",
                    "properties": {
                        "kind": {"type": "string", "enum": ["cat"]},
                        "meow": {"type": "boolean"},
                    },
                    "required": ["kind", "meow"],
                },
                "Dog": {
                    "type": "object",
                    "properties": {
                        "kind": {"type": "string", "enum": ["dog"]},
                        "bark": {"type": "boolean"},
                    },
                    "required": ["kind", "bark"],
                },
                "Pet": {
                    "oneOf": [
                        {"$ref": "#/components/schemas/Cat"},
                        {"$ref": "#/components/schemas/Dog"},
                    ],
                    "discriminator": {
                        "propertyName": "kind",
                        "mapping": {
                            "cat": "#/components/schemas/Cat",
                            "dog": "#/components/schemas/Dog",
                        },
                    },
                },
            }
        },
    }


def test_nullable_string() -> None:
    schema = {"type": "string", "nullable": True}
    validate(None, schema, cls=OAS30Validator)
    validate("ok", schema, cls=OAS30Validator)


def test_invalid_type() -> None:
    with pytest.raises(ValidationError):
        validate(1, {"type": "string", "nullable": True}, cls=OAS30Validator)


def test_discriminator_local_dict() -> None:
    validate({"kind": "cat", "meow": True}, PET_SCHEMA, cls=OAS30Validator)
    validate({"kind": "dog", "bark": False}, PET_SCHEMA, cls=OAS30Validator)
