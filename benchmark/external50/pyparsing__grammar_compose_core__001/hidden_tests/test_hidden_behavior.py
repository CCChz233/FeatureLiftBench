from __future__ import annotations

import re
from pathlib import Path

from featurelifted import (
    Group,
    Keyword,
    OneOrMore,
    ParseException,
    Regex,
    Suppress,
    Word,
    ZeroOrMore,
    alphas,
    nums,
)


def test_keyword_and_regex() -> None:
    grammar = Keyword("select") + Regex(r"[a-z]+")("col")
    assert grammar.parse_string("select name").as_dict()["col"] == "name"


def test_zero_one_or_more() -> None:
    grammar = Word(alphas) + ZeroOrMore(Suppress(",") + Word(alphas))
    assert grammar.parse_string("a,b,c").as_list() == ["a", "b", "c"]
    grammar2 = OneOrMore(Word(nums))
    assert grammar2.parse_string("1 2 3").as_list() == ["1", "2", "3"]


def test_group_structure() -> None:
    grammar = Group(Word(alphas) + Word(nums))
    result = grammar.parse_string("x 9")
    assert result.as_list() == [["x", "9"]]


def test_parse_all_flag() -> None:
    grammar = Word(alphas)
    try:
        grammar.parse_string("ab cd", parse_all=True)
        assert False
    except ParseException:
        pass


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\s*(?:from pyparsing\b|import pyparsing\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
