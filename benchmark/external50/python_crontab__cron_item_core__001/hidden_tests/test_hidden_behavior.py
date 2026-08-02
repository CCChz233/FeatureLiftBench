from __future__ import annotations

import re
from pathlib import Path


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from crontab\\b|import crontab\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path


from featurelifted import CronItem, CronSlices


def test_slices_setall() -> None:
    slices = CronSlices()
    slices.setall("0", "12", "*", "*", "1")
    assert "0" in slices.render() and "12" in slices.render()


def test_special_reboot() -> None:
    slices = CronSlices("@reboot")
    assert "@reboot" in slices.render() or slices.special == "@reboot"
