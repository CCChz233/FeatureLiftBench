from __future__ import annotations

from featurelifted import (
    Bool,
    Int,
    Map,
    MapPattern,
    Optional,
    Seq,
    Str,
    YAMLValidationError,
    load,
)


def test_load_map_seq() -> None:
    schema = Map(
        {
            "name": Str(),
            "age": Int(),
            "tags": Seq(Str()),
            "enabled": Bool(),
            Optional("nick"): Str(),
        }
    )
    doc = load("name: Ada\nage: 3\ntags:\n  - a\n  - b\nenabled: yes", schema)
    assert doc.data == {"name": "Ada", "age": 3, "tags": ["a", "b"], "enabled": True}


def test_validation_error() -> None:
    try:
        load("name: Ada\nage: x", Map({"name": Str(), "age": Int()}))
        assert False, "expected YAMLValidationError"
    except YAMLValidationError:
        pass


def test_map_pattern() -> None:
    doc = load("a: 1\nb: 2", MapPattern(Str(), Int()))
    assert doc.data == {"a": 1, "b": 2}
