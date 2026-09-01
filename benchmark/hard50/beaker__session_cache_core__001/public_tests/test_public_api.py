from __future__ import annotations

from featurelifted import CacheManager, Session


def test_memory_session_roundtrip() -> None:
    session = Session({}, use_cookies=False, type="memory")
    session["user"] = "ada"
    session.save()
    loaded = Session({}, id=session.id, use_cookies=False, type="memory")
    assert loaded["user"] == "ada"


def test_memory_cache_put_get() -> None:
    manager = CacheManager(type="memory")
    cache = manager.get_cache("ns")
    cache.put("k", 42)
    assert cache.get("k") == 42
