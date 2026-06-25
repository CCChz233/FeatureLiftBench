from __future__ import annotations

import re

from featurelifted import slugify
from featurelifted import smart_truncate


def test_html_entity_decimal_and_hexadecimal_handling() -> None:
    assert slugify("foo &amp; bar") == "foo-bar"
    assert slugify("foo &amp; bar", entities=False) == "foo-amp-bar"
    assert slugify("&#381;", decimal=True) == "z"
    assert slugify("&#381;", entities=False, decimal=False) == "381"
    assert slugify("&#x17D;", hexadecimal=True) == "z"
    assert slugify("&#x17D;", hexadecimal=False) == "x17d"


def test_allow_unicode_preserves_non_ascii_words() -> None:
    assert slugify("影師嗎", allow_unicode=True) == "影師嗎"
    assert slugify("C'est déjà l'été.", allow_unicode=True) == "c-est-déjà-l-été"
    assert slugify("Компьютер", allow_unicode=True) == "компьютер"


def test_replacements_regex_and_number_cleanup() -> None:
    assert slugify("10 | 20 %", replacements=[["|", "or"], ["%", "percent"]]) == "10-or-20-percent"
    assert slugify("I ♥ 🦄", replacements=[["♥", "amour"], ["🦄", "licorne"]]) == "i-amour-licorne"
    assert slugify("1,000 reasons you are #1") == "1000-reasons-you-are-1"

    pattern = re.compile(r"[^-a-z0-9_]+")
    assert slugify("___This is a test___", regex_pattern=pattern) == "___this-is-a-test___"


def test_case_sensitive_stopwords_and_save_order() -> None:
    assert slugify(
        "thIs Has a stopword Stopword",
        stopwords=["Stopword"],
        lowercase=False,
    ) == "thIs-Has-a-stopword"
    assert slugify(
        "one two three four five",
        max_length=12,
        word_boundary=True,
        save_order=False,
    ) == "one-two-four"
    assert slugify(
        "one two three four five",
        max_length=12,
        word_boundary=True,
        save_order=True,
    ) == "one-two"


def test_smart_truncate_edges() -> None:
    assert smart_truncate("alpha beta gamma", max_length=0) == "alpha beta gamma"
    assert smart_truncate("alpha", max_length=20) == "alpha"
    assert smart_truncate("alphabet", max_length=5, word_boundary=True) == "alpha"
    assert smart_truncate("alpha beta gamma", max_length=10, word_boundary=True, save_order=True) == "alpha beta"
