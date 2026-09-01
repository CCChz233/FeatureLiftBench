from __future__ import annotations

from featurelifted import Field, Int, ObjectType, Schema, String


class Patron(ObjectType):
    id = String()
    name = String()
    age = Int()


class Query(ObjectType):
    hello = String(name=String(default_value="world"))
    patron = Field(Patron)

    def resolve_hello(root, info, name):
        return f"Hello {name}"

    def resolve_patron(root, info):
        return Patron(id="1", name="Ada", age=36)


def test_default_argument_resolver() -> None:
    result = Schema(query=Query).execute("{ hello }")
    assert result.errors is None
    assert result.data == {"hello": "Hello world"}


def test_explicit_argument() -> None:
    result = Schema(query=Query).execute('{ hello(name: "Ada") }')
    assert result.errors is None
    assert result.data == {"hello": "Hello Ada"}


def test_nested_object_field() -> None:
    result = Schema(query=Query).execute("{ patron { id name age } }")
    assert result.errors is None
    assert result.data == {"patron": {"id": "1", "name": "Ada", "age": 36}}


def test_unknown_field_reports_errors() -> None:
    result = Schema(query=Query).execute("{ nope }")
    assert result.data is None
    assert result.errors
