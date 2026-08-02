from __future__ import annotations

from featurelifted import Group, Literal, Optional, ParseException, Word, alphas


def test_word_literal_compose() -> None:
    grammar = Word(alphas)("name") + Literal(",") + Word(alphas)("item")
    result = grammar.parse_string("Hello, world")
    assert result.as_dict()["name"] == "Hello"
    assert result.as_list()[0] == "Hello"


def test_optional_group() -> None:
    grammar = Word(alphas) + Optional(Literal("!")("bang"))
    assert grammar.parse_string("hi").as_list() == ["hi"]
    assert "bang" in grammar.parse_string("hi!").as_dict()


def test_parse_exception() -> None:
    grammar = Literal("OK")
    try:
        grammar.parse_string("NO")
        assert False, "expected ParseException"
    except ParseException as exc:
        assert exc.loc >= 0
