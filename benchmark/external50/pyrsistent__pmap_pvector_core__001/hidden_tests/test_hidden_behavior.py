from __future__ import annotations

import re
from pathlib import Path

from featurelifted import pmap, pvector


def test_pmap_immutability() -> None:
    m = pmap({"x": 1})
    m2 = m.set("y", 2)
    assert "y" not in m and m2["y"] == 2


def test_pvector_set() -> None:
    v = pvector([10, 20, 30])
    v2 = v.set(1, 99)
    assert list(v) == [10, 20, 30] and list(v2) == [10, 99, 30]


def test_pvector_extend() -> None:
    base = pvector([1])
    extended = base.extend([2, 3])
    assert list(extended) == [1, 2, 3]


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\s*(?:from pyrsistent\b|import pyrsistent\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
