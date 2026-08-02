from __future__ import annotations

from datetime import datetime

from featurelifted import freeze_time


def test_freeze_context_manager() -> None:
    with freeze_time("2020-01-15 12:00:00"):
        assert datetime.now().year == 2020
        assert datetime.now().month == 1
        assert datetime.now().day == 15


def test_freeze_decorator() -> None:
    @freeze_time("2019-06-01")
    def stamped() -> int:
        return datetime.now().year

    assert stamped() == 2019


def test_unfrozen_after_context() -> None:
    real_year = datetime.now().year
    with freeze_time("2001-01-01"):
        assert datetime.now().year == 2001
    assert datetime.now().year == real_year
