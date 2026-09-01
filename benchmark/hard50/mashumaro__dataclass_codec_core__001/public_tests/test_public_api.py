from __future__ import annotations

from dataclasses import dataclass, field

import pytest
from featurelifted import DataClassDictMixin, MissingField, field_options
from featurelifted.config import BaseConfig


@dataclass
class Addr(DataClassDictMixin):
    city: str


@dataclass
class Person(DataClassDictMixin):
    name: str = field(metadata=field_options(alias="fullName"))
    addr: Addr
    title: str | None = None

    class Config(BaseConfig):
        serialize_by_alias = True
        omit_none = True


def test_nested_roundtrip() -> None:
    person = Person.from_dict({"fullName": "Ada", "addr": {"city": "Paris"}, "title": "Dr"})
    assert person.name == "Ada"
    assert person.addr.city == "Paris"
    assert person.to_dict()["addr"]["city"] == "Paris"


def test_alias_and_omit_none() -> None:
    person = Person.from_dict({"fullName": "Lin", "addr": {"city": "Oslo"}})
    payload = person.to_dict()
    assert payload["fullName"] == "Lin"
    assert "name" not in payload
    assert "title" not in payload


def test_missing_required_raises() -> None:
    with pytest.raises(MissingField):
        Person.from_dict({"addr": {"city": "Paris"}})
