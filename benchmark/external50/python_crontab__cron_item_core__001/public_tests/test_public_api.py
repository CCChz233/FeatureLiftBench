from __future__ import annotations

from featurelifted import CronItem, CronSlices


def test_cron_slices_valid() -> None:
    assert CronSlices.is_valid("* * * * *")
    slices = CronSlices("* * * * *")
    assert slices.render().startswith("*")


def test_cron_item_from_line() -> None:
    item = CronItem("* * * * * /bin/echo hi")
    assert item.is_valid()
    rendered = item.render()
    assert "/bin/echo" in rendered or "echo" in rendered
    assert item.is_enabled()


def test_cron_item_invalid_line() -> None:
    assert not CronSlices.is_valid("not five fields")
