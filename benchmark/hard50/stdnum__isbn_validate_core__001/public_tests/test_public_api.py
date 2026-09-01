from __future__ import annotations

from featurelifted.isbn import compact, validate


def test_validate_isbn13() -> None:
    assert validate("978-9024538270") == "9789024538270"


def test_compact_isbn10() -> None:
    assert compact("1-85798-218-5") == "1857982185"
