from __future__ import annotations

import datetime
import re
from pathlib import Path

import pytest

from featurelifted import DAILY, FR, MONTHLY, YEARLY, rrule, rruleset, rrulestr


def test_bysetpos_last_friday() -> None:
    start = datetime.datetime(2020, 1, 1)
    got = list(rrule(MONTHLY, dtstart=start, byweekday=FR(-1), count=3))
    assert all(value.weekday() == 4 for value in got)
    assert got[:2] == [datetime.datetime(2020, 1, 31), datetime.datetime(2020, 2, 28)]


def test_byeaster_occurrence() -> None:
    got = list(rrule(YEARLY, dtstart=datetime.datetime(2020, 1, 1), byeaster=1, count=2))
    assert len(got) == 2
    assert (got[0].month, got[0].day) == (4, 13)


def test_rruleset_exdate_skips() -> None:
    start = datetime.datetime(2020, 1, 1)
    rules = rruleset()
    rules.rrule(rrule(DAILY, dtstart=start, count=3))
    rules.exdate(datetime.datetime(2020, 1, 2))
    assert list(rules) == [datetime.datetime(2020, 1, 1), datetime.datetime(2020, 1, 3)]


def test_interval_and_until_boundaries() -> None:
    start = datetime.datetime(2020, 1, 1)
    end = datetime.datetime(2020, 1, 6)
    assert list(rrule(DAILY, dtstart=start, interval=2, until=end)) == [
        datetime.datetime(2020, 1, 1),
        datetime.datetime(2020, 1, 3),
        datetime.datetime(2020, 1, 5),
    ]


def test_rruleset_rdate_includes_explicit_date() -> None:
    start = datetime.datetime(2020, 1, 1)
    rules = rruleset()
    rules.rrule(rrule(DAILY, dtstart=start, count=2))
    rules.rdate(datetime.datetime(2020, 1, 10))
    assert list(rules) == [
        datetime.datetime(2020, 1, 1),
        datetime.datetime(2020, 1, 2),
        datetime.datetime(2020, 1, 10),
    ]


def test_invalid_rrulestr_freq_raises() -> None:
    with pytest.raises(ValueError):
        rrulestr(
            "RRULE:FREQ=NOTAFREQ;COUNT=1",
            dtstart=datetime.datetime(2020, 1, 1),
            ignoretz=True,
        )


def test_rrulestr_byday_token() -> None:
    rule = rrulestr(
        "RRULE:FREQ=MONTHLY;BYDAY=1MO;COUNT=2",
        dtstart=datetime.datetime(2020, 1, 1),
        ignoretz=True,
    )
    got = list(rule)
    assert len(got) == 2
    assert got[0].weekday() == 0


def test_no_dateutil_import_surface() -> None:
    import featurelifted

    forbidden = {"parser", "tz", "relativedelta", "zoneinfo"}
    exports = set(getattr(featurelifted, "__all__", []))
    for name in forbidden:
        assert name not in exports, f"unexpected export: {name}"
    pkg_root = Path(featurelifted.__file__).parent
    import_pattern = re.compile(r"^\s*(?:from dateutil|import dateutil)\b", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not import_pattern.search(path.read_text(encoding="utf-8"))
