from __future__ import annotations

from featurelifted import TLDExtract


def test_registered_domain() -> None:
    ext = TLDExtract(suffix_list_urls=())
    result = ext("https://foo.bar.co.uk")
    assert f"{result.domain}.{result.suffix}" == "bar.co.uk"


def test_no_subdomain() -> None:
    ext = TLDExtract(suffix_list_urls=())
    result = ext("example.com")
    assert result.subdomain == ""
    assert result.domain == "example"
    assert result.suffix == "com"


def test_no_upstream_import_surface() -> None:
    import re
    from pathlib import Path
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(
        rf"^\s*(?:from tldextract\b|import tldextract\b)",
        re.MULTILINE,
    )
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
