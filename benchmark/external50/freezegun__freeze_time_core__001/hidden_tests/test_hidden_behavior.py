from __future__ import annotations

import re
from pathlib import Path


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\\s*(?:from freezegun\\b|import freezegun\\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path


from datetime import datetime, timedelta

from featurelifted import freeze_time


def test_tick_moves_time() -> None:
    with freeze_time("2020-01-01 00:00:00", tick=True) as frozen:
        t0 = datetime.now()
        frozen.tick(delta=timedelta(hours=1))
        t1 = datetime.now()
        assert t1 > t0
        assert t1.hour == 1


def test_move_to() -> None:
    with freeze_time("2020-01-01") as frozen:
        frozen.move_to("2021-12-25")
        assert datetime.now().year == 2021
        assert datetime.now().month == 12
