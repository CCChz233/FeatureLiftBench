from featurelifted import Language, standardize_tag


def test_standardize_and_language_object():
    assert standardize_tag("eng_US") == "en-US"
    language = Language.get("zh-cmn-Hant")
    assert language.to_tag() == "zh-Hant"


def test_cldr_name_and_maximize():
    assert Language.get("fr").language_name("en") == "French"
    assert Language.get("zh-TW").maximize().script == "Hant"
