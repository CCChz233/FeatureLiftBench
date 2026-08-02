from __future__ import annotations

from datetime import datetime

from featurelifted import Calendar, Event


def test_event_dtend() -> None:
    cal = Calendar()
    event = Event()
    event.add("summary", "All day")
    event.add("dtstart", datetime(2024, 1, 1, 0, 0, 0))
    event.add("dtend", datetime(2024, 1, 2, 0, 0, 0))
    cal.add_component(event)
    parsed = Calendar.from_ical(cal.to_ical())
    ev = parsed.subcomponents[0]
    assert "dtend" in ev


def test_multiple_events() -> None:
    cal = Calendar()
    for name in ("a", "b"):
        ev = Event()
        ev.add("summary", name)
        cal.add_component(ev)
    parsed = Calendar.from_ical(cal.to_ical())
    summaries = [c["summary"].to_ical().decode() for c in parsed.subcomponents]
    assert summaries == ["a", "b"]


def test_no_upstream_import_surface() -> None:
    import re
    from pathlib import Path
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(
        rf"^\s*(?:from icalendar\b|import icalendar\b)",
        re.MULTILINE,
    )
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
