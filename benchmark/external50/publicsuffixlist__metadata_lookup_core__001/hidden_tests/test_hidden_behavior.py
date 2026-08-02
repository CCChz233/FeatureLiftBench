from featurelifted import PublicSuffixList


def test_custom_wildcard_and_exception_rules():
    psl = PublicSuffixList("*.example\n!city.example\n")
    assert psl.publicsuffix("a.example") == "a.example"
    assert psl.publicsuffix("city.example") == "example"


def test_unknown_suffix_policy():
    strict = PublicSuffixList("com\n", accept_unknown=False)
    assert strict.publicsuffix("host.unknown") is None


def test_bundled_resource_is_available_offline():
    psl = PublicSuffixList()
    assert psl.publicsuffix("www.example.co.uk") == "co.uk"


def test_required_api_surface():
    from featurelifted import PublicSuffixList
    assert isinstance(PublicSuffixList, type)
    assert all(callable(getattr(PublicSuffixList, n)) for n in ('publicsuffix', 'privatesuffix', 'is_public', 'is_private'))


def test_no_upstream_import_surface():
    import re
    from pathlib import Path
    import featurelifted
    pattern = re.compile(r"^\s*(?:from publicsuffixlist|import publicsuffixlist)\b", re.MULTILINE)
    for path in Path(featurelifted.__file__).parent.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8"))
