from __future__ import annotations

from datetime import datetime

from featurelifted import Settings, detect_languages, parse


def test_parse_iso_and_english() -> None:
    assert parse("2020-01-15") == datetime(2020, 1, 15, 0, 0)
    assert parse("January 15, 2020") == datetime(2020, 1, 15, 0, 0)


def test_parse_with_languages() -> None:
    es = parse("15 de enero de 2020", languages=["es"])
    fr = parse("15 janvier 2020", languages=["fr"])
    assert es is not None and es.year == 2020 and es.month == 1 and es.day == 15
    assert fr is not None and fr.year == 2020 and fr.month == 1 and fr.day == 15


def test_settings_timezone_aware() -> None:
    settings = Settings(
        {
            "RETURN_AS_TIMEZONE_AWARE": True,
            "TIMEZONE": "UTC",
            "TO_TIMEZONE": "UTC",
        }
    )
    dt = parse("2020-01-15 12:00:00", settings=settings)
    assert dt is not None
    assert dt.tzinfo is not None
