import pytest

from featurelifted import (
    WheelError,
    parse_wheel_filename,
    safe_extra,
    safe_name,
    split_sections,
    urlsafe_b64encode,
)


def test_split_sections_and_b64():
    sections = split_sections("readme\n\n[metadata]\nname=demo\n\n[files]\nREADME")
    assert sections == [
        (None, ["readme"]),
        ("metadata", ["name=demo"]),
        ("files", ["README"]),
    ]
    assert urlsafe_b64encode(b"abc") == b"YWJj"


def test_parse_wheel_filename():
    assert parse_wheel_filename("my_pkg-1.0.0-py3-none-any.whl") == ("my-pkg", "1.0.0", "")
    assert parse_wheel_filename("my_pkg-1.0.0-2-py3-none-any.whl") == ("my-pkg", "1.0.0", "2")
    with pytest.raises(WheelError):
        parse_wheel_filename("not-a-wheel.txt")


def test_safe_name_extra_hidden():
    assert safe_name("My Project.Plugin") == "My-Project.Plugin"
    assert safe_extra("Dev Tools.Plugin") == "dev_tools.plugin"
