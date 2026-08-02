from __future__ import annotations

from featurelifted import TLDExtract, extract


def test_tldextract_offline() -> None:
    ext = TLDExtract(suffix_list_urls=())
    result = ext("https://www.google.co.uk/path")
    assert result.subdomain == "www"
    assert result.domain == "google"
    assert result.suffix == "co.uk"


def test_extract_convenience() -> None:
    ext = TLDExtract(suffix_list_urls=())
    result = ext("blog.example.com")
    assert result.domain == "example"
    assert result.suffix == "com"
