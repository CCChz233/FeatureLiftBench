from featurelifted import Language, best_match, standardize_tag


def test_deprecated_tag_normalization():
    assert standardize_tag("en-uk") == "en-GB"


def test_hidden_cldr_name_lookup():
    assert Language.get("de").language_name("en") == "German"


def test_best_match_prefers_closest_supported_tag():
    match, score = best_match("en-AU", ["fr", "en-GB", "de"])
    assert match == "en-GB" and score > 0


def test_required_api_surface():
    from featurelifted import Language, best_match, standardize_tag
    assert isinstance(Language, type)
    assert all(callable(getattr(Language, n)) for n in ('get', 'to_tag', 'language_name', 'maximize'))
    assert callable(standardize_tag) and callable(best_match)


def test_no_upstream_import_surface():
    import re
    from pathlib import Path
    import featurelifted
    pattern = re.compile(r"^\s*(?:from langcodes|import langcodes)\b", re.MULTILINE)
    for path in Path(featurelifted.__file__).parent.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8"))
