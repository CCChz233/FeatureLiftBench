from __future__ import annotations

from featurelifted import DictCache, ExpiresAfter, Serializer


def test_dict_cache_roundtrip() -> None:
    cache = DictCache()
    cache.set("k", b"value")
    assert cache.get("k") == b"value"
    cache.delete("k")
    assert cache.get("k") is None


def test_expires_after_construct() -> None:
    h = ExpiresAfter(days=1, hours=2)
    assert h is not None


def test_serializer_construct() -> None:
    assert Serializer() is not None
