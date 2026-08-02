from __future__ import annotations

from featurelifted import Version


def test_parse_basic() -> None:
    v = Version.parse("1.2.3")
    assert str(v) == "1.2.3"
    assert v.major == 1 and v.minor == 2 and v.patch == 3


def test_compare_and_order() -> None:
    a = Version.parse("1.2.3")
    b = Version.parse("1.2.4")
    assert a.compare(b) == -1
    assert a < b
    assert a != b


def test_bump_and_replace() -> None:
    v = Version.parse("1.2.3")
    assert str(v.bump_major()) == "2.0.0"
    assert str(v.bump_minor()) == "1.3.0"
    assert str(v.bump_patch()) == "1.2.4"
    assert str(v.replace(prerelease="rc.1")) == "1.2.3-rc.1"
