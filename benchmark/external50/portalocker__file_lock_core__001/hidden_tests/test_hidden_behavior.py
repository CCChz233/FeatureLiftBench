from __future__ import annotations

import re
from pathlib import Path

from featurelifted import LOCK_EX, LOCK_NB, LOCK_SH, Lock, LockException


def test_lock_constants() -> None:
    assert LOCK_EX is not None and LOCK_SH is not None and LOCK_NB is not None


def test_lock_exception_type() -> None:
    assert issubclass(LockException, Exception)


def test_lock_timeout(tmp_path) -> None:
    path = tmp_path / "t.txt"
    path.write_text("z", encoding="utf-8")
    with Lock(str(path), timeout=1):
        assert path.exists()


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\s*(?:from portalocker\b|import portalocker\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
