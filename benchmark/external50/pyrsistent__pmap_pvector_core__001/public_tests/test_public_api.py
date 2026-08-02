from __future__ import annotations

from featurelifted import PMap, PVector, pmap, pvector


def test_pmap_set_get() -> None:
    m = pmap({"a": 1})
    m2 = m.set("b", 2)
    assert m2["a"] == 1 and m2.get("b") == 2
    assert m is not m2


def test_pvector_append() -> None:
    v = pvector([1, 2])
    v2 = v.append(3)
    assert list(v) == [1, 2] and list(v2) == [1, 2, 3]
    assert v is not v2


def test_factory_types() -> None:
    assert isinstance(pmap(), PMap)
    assert isinstance(pvector(), PVector)
