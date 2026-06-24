from __future__ import annotations

from textwrap import dedent

import pytest

from featurelifted import COMMENTCHARS
from featurelifted import IniConfig
from featurelifted import ParseError
from featurelifted import iscommentline


def test_basic_parse_iteration_and_lookup() -> None:
    config = IniConfig(
        "sample.ini",
        data=dedent(
            """
            [section1]
            name1 = value1
            name2: value2

            [section2]
            enabled = yes
            """
        ),
    )

    sections = list(config)

    assert [section.name for section in sections] == ["section1", "section2"]
    assert config["section1"]["name1"] == "value1"
    assert config["section1"]["name2"] == "value2"
    assert config.get("section2", "enabled") == "yes"
    assert "section1" in config
    assert "missing" not in config


def test_get_default_conversion_and_section_wrapper() -> None:
    config = IniConfig("sample.ini", data="[main]\ncount = 3\nratio = 1.5\n")

    assert config.get("main", "count", convert=int) == 3
    assert config.get("main", "missing", default="fallback") == "fallback"
    assert config["main"].get("ratio", convert=float) == 1.5
    assert list(config["main"].items()) == [("count", "3"), ("ratio", "1.5")]


def test_line_numbers_and_parse_errors() -> None:
    config = IniConfig(
        "sample.ini",
        data="[first]\nvalue = 1\n# comment\n[second]\nvalue = 2\n",
    )

    assert config.lineof("first") == 1
    assert config.lineof("first", "value") == 2
    assert config.lineof("second") == 4
    assert config.lineof("missing") is None

    with pytest.raises(ParseError) as excinfo:
        IniConfig("broken.ini", data="value = 1\n")

    assert str(excinfo.value) == "broken.ini:1: no section header defined"


def test_comments_and_exported_constants() -> None:
    assert COMMENTCHARS == "#;"
    assert iscommentline("# full comment")
    assert iscommentline("  ; indented comment")
    assert not iscommentline("name = value # inline comment")
