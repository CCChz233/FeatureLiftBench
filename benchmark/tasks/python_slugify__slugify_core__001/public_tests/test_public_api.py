from __future__ import annotations

from featurelifted import slugify
from featurelifted import smart_truncate


def test_basic_ascii_and_separator_cleanup() -> None:
    assert slugify("Hello World") == "hello-world"
    assert slugify("This -- is a ## test ---") == "this-is-a-test"
    assert slugify("___This is a test___") == "this-is-a-test"


def test_transliteration_and_accents() -> None:
    assert slugify("C'est déjà l'été.") == "c-est-deja-l-ete"
    assert slugify("影師嗎") == "ying-shi-ma"
    assert slugify("Компьютер") == "kompiuter"


def test_options_for_separator_stopwords_and_truncation() -> None:
    text = "the quick brown fox jumps over the lazy dog"
    assert slugify(text, stopwords=["the"]) == "quick-brown-fox-jumps-over-lazy-dog"
    assert slugify("jaja---lol-méméméoo--a", max_length=9) == "jaja-lol"
    assert slugify("jaja---lol-méméméoo--a", separator=".") == "jaja.lol.mememeoo.a"


def test_smart_truncate_public_api() -> None:
    assert smart_truncate("one two three", max_length=7) == "one two"
    assert smart_truncate("one two three", max_length=7, word_boundary=True) == "one two"
