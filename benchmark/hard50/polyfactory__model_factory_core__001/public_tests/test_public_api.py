from __future__ import annotations

from dataclasses import dataclass

from featurelifted import DataclassFactory, Use


@dataclass
class Address:
    city: str


@dataclass
class Person:
    name: str
    age: int
    address: Address


class PersonFactory(DataclassFactory[Person]):
    name = Use(lambda: "fixed")


def test_build_generates_typed_dataclass() -> None:
    person = PersonFactory.build()
    assert isinstance(person, Person)
    assert person.name == "fixed"
    assert isinstance(person.age, int)
    assert isinstance(person.address, Address)
    assert isinstance(person.address.city, str)


def test_build_overrides() -> None:
    person = PersonFactory.build(age=41, name="Ada")
    assert person.age == 41
    assert person.name == "Ada"


def test_use_field_and_batch() -> None:
    people = PersonFactory.batch(3, age=7)
    assert len(people) == 3
    assert all(item.age == 7 for item in people)
    assert all(item.name == "fixed" for item in people)
