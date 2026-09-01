from __future__ import annotations

from dataclasses import dataclass

import pytest
from featurelifted import ValidationError, deserialize, deserializer, serialize, validator


@deserializer
class Even:
    def __init__(self, n: int) -> None:
        if n % 2:
            raise ValueError("odd")
        self.n = n


@dataclass
class User:
    age: int
    name: str = "anon"

    @validator
    def age_ok(self):
        if self.age < 0:
            yield "age must be >= 0"


def test_dataclass_roundtrip() -> None:
    user = deserialize(User, {"age": 3})
    assert user == User(age=3, name="anon")
    assert serialize(user) == {"age": 3, "name": "anon"}


def test_validator_rejects_negative_age() -> None:
    with pytest.raises(ValidationError):
        deserialize(User, {"age": -1})


def test_deserializer_conversion() -> None:
    even = deserialize(Even, 4)
    assert even.n == 4
    with pytest.raises(Exception):
        deserialize(Even, 3)
