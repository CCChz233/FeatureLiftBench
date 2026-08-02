from __future__ import annotations

from featurelifted import PackageURL


def test_from_string_fields() -> None:
    purl = PackageURL.from_string("pkg:npm/%40scope/foo@1.2.3?a=b#section")
    assert purl.type == "npm"
    assert purl.namespace == "@scope"
    assert purl.name == "foo"
    assert purl.version == "1.2.3"


def test_to_string_roundtrip() -> None:
    original = "pkg:pypi/django@4.2.0"
    purl = PackageURL.from_string(original)
    assert purl.to_string() == original


def test_constructor() -> None:
    purl = PackageURL(type="gem", name="rails", version="7.0.0")
    assert "pkg:gem/rails@7.0.0" == purl.to_string()
