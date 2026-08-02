from __future__ import annotations

import re
from pathlib import Path

import pytest
from featurelifted import Version


def test_prerelease_and_build_parse() -> None:
    v = Version.parse("1.0.0-alpha.1+build.7")
    assert v.prerelease == "alpha.1"
    assert v.build == "build.7"
    assert str(v) == "1.0.0-alpha.1+build.7"


def test_invalid_version_raises() -> None:
    with pytest.raises(ValueError):
        Version.parse("not-a-version")


def test_constructor_defaults() -> None:
    v = Version(2)
    assert str(v) == "2.0.0"


def test_ordering_operators() -> None:
    assert Version.parse("1.0.0") <= Version.parse("1.0.0")
    assert Version.parse("2.0.0") >= Version.parse("1.9.9")


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\s*(?:from semver|import semver)\b", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8"))
