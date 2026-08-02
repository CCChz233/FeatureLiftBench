from __future__ import annotations

from datetime import datetime

from featurelifted import Calendar, Event


def test_build_and_roundtrip() -> None:
    cal = Calendar()
    event = Event()
    event.add("summary", "Team sync")
    event.add("dtstart", datetime(2024, 6, 1, 9, 0, 0))
    cal.add_component(event)
    raw = cal.to_ical()
    parsed = Calendar.from_ical(raw)
    ev = parsed.subcomponents[0]
    assert ev["summary"].to_ical().decode() == "Team sync"


def test_parse_existing_ics() -> None:
    ics = (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//FeatureLiftBench//EN\r\n"
        "BEGIN:VEVENT\r\n"
        "SUMMARY:Demo\r\n"
        "DTSTART:20240101T100000\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )
    cal = Calendar.from_ical(ics)
    assert cal["prodid"].to_ical().decode().startswith("-//")
