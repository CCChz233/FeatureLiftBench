from __future__ import annotations

import re
from pathlib import Path


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from packageurl\\b|import packageurl\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path


import pytest
from featurelifted import PackageURL


def test_qualifiers_normalize() -> None:
    purl = PackageURL.from_string("pkg:nuget/Newtonsoft.Json@13.0.1?arch=x86&os=windows")
    text = purl.to_string()
    assert "arch=x86" in text and "os=windows" in text


def test_invalid_purl() -> None:
    with pytest.raises(ValueError):
        PackageURL.from_string("not-a-purl")
