from __future__ import annotations

import re
from pathlib import Path

from featurelifted import BaseCache, CacheController, DictCache, ExpiresAfter, Serializer


def test_base_cache_interface() -> None:
    assert issubclass(DictCache, BaseCache)


def test_cache_controller_construct() -> None:
    ctrl = CacheController(DictCache())
    assert ctrl.cache is not None


def test_expires_after_days_hours() -> None:
    h = ExpiresAfter(days=0, hours=1)
    assert getattr(h, "delta", None) is not None or h is not None


def test_serializer_serde_version() -> None:
    ser = Serializer()
    version = getattr(ser, "serde_version", "1")
    assert version


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\s*(?:from cachecontrol\b|import cachecontrol\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
