from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from featurelifted import IniConfig
from featurelifted import ParseError


def test_multiline_values_and_file_order() -> None:
    config = IniConfig(
        "pypirc",
        data=dedent(
            """
            [distutils]
            index-servers =
                pypi
                internal

            [pypi]
            repository: https://upload.pypi.org/legacy/
            username = alice
            """
        ),
    )

    distutils, pypi = list(config)

    assert distutils.name == "distutils"
    assert pypi.name == "pypi"
    assert distutils["index-servers"] == "pypi\ninternal"
    assert list(pypi.items()) == [
        ("repository", "https://upload.pypi.org/legacy/"),
        ("username", "alice"),
    ]


def test_parse_strips_inline_comments_by_default() -> None:
    config = IniConfig.parse(
        "comments.ini",
        data=dedent(
            """
            [main]
            name = value # removed
            other = second ; also removed
            list =
                alpha # removed
                beta ; also removed
            """
        ),
    )

    assert config["main"]["name"] == "value"
    assert config["main"]["other"] == "second"
    assert config["main"]["list"] == "alpha\nbeta"


def test_parse_can_preserve_inline_comments() -> None:
    config = IniConfig.parse(
        "comments.ini",
        data="[main]\nname = value # preserved\n",
        strip_inline_comments=False,
    )

    assert config["main"]["name"] == "value # preserved"


def test_duplicate_section_and_key_errors() -> None:
    with pytest.raises(ParseError) as section_error:
        IniConfig("dup.ini", data="[main]\n[main]\n")
    assert "duplicate section 'main'" in str(section_error.value)
    assert section_error.value.lineno == 1

    with pytest.raises(ParseError) as key_error:
        IniConfig("dup.ini", data="[main]\nname = alice\nname = bob\n")
    assert "duplicate name 'name'" in str(key_error.value)
    assert key_error.value.lineno == 2


def test_unicode_whitespace_and_section_name_opt_in() -> None:
    config = IniConfig(
        "unicode.ini",
        data="[main]\nkey\u00a0 = \u00a0value\u00a0\n",
    )

    assert config["main"]["key"] == "value"

    stripped = IniConfig.parse(
        "unicode.ini",
        data="[main\u00a0]\nkey = value\n",
        strip_section_whitespace=True,
    )
    assert "main" in stripped
    assert stripped["main"]["key"] == "value"


def test_reads_from_path_when_data_is_omitted(tmp_path: Path) -> None:
    path = tmp_path / "config.ini"
    path.write_text("[main]\nname = value\n", encoding="utf-8")

    config = IniConfig(path)

    assert config.path == str(path)
    assert config["main"]["name"] == "value"
