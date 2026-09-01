from dataclasses import dataclass
from typing import TypedDict, Union

import pytest
from featurelifted import dump, load
from featurelifted.exceptions import TypedloadException


@dataclass
class Addr:
    city: str


@dataclass
class Person:
    name: str
    addr: Addr
    age: int = 0


class Point(TypedDict):
    x: int
    y: int


def test_dataclass_roundtrip() -> None:
    person = load({"name": "Ada", "addr": {"city": "Paris"}}, Person)
    assert person.name == "Ada" and person.addr.city == "Paris"
    assert dump(person)["addr"]["city"] == "Paris"


def test_union_and_typeddict() -> None:
    assert load(1, Union[int, str]) == 1
    assert load("q", Union[int, str]) == "q"
    assert load({"x": 1, "y": 2}, Point) == {"x": 1, "y": 2}


def test_failonextra() -> None:
    with pytest.raises(TypedloadException):
        load({"name": "Ada", "addr": {"city": "P"}, "extra": 1}, Person, failonextra=True)
