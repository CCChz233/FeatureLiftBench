from __future__ import annotations

import re
from pathlib import Path

import pytest
from featurelifted import Settings, detect_languages, parse


def test_detect_languages_es_fr() -> None:
    es = detect_languages("15 de enero de 2020", languages=["en", "es", "fr"])
    fr = detect_languages("15 janvier 2020", languages=["en", "es", "fr"])
    assert "es" in es
    assert "fr" in fr


def test_prefer_dates_from_past() -> None:
    settings = Settings({"PREFER_DATES_FROM": "past"})
    assert parse("2020-01-15", settings=settings) is not None


def test_date_order_dmy() -> None:
    settings = Settings({"DATE_ORDER": "DMY", "STRICT_PARSING": False})
    dt = parse("15/01/2020", settings=settings)
    assert dt is not None
    assert dt.day == 15 and dt.month == 1 and dt.year == 2020


def test_invalid_settings_key() -> None:
    with pytest.raises(TypeError):
        Settings({"PREFER_DATES_FROM": None})


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\s*(?:from dateparser\b|import dateparser\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
