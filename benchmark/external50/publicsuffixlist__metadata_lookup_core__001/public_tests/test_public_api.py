from featurelifted import PublicSuffixList


def test_bundled_list_resolves_common_suffixes():
    psl = PublicSuffixList()
    assert psl.publicsuffix("www.example.co.uk") == "co.uk"
    assert psl.privatesuffix("www.example.co.uk") == "example.co.uk"


def test_public_and_private_classification():
    psl = PublicSuffixList()
    assert psl.is_public("com")
    assert psl.is_private("example.com")
