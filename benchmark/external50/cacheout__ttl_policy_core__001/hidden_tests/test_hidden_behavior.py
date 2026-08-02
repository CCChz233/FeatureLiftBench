from featurelifted import Cache, LRUCache


def test_configure_changes_default_ttl():
    class Timer:
        now = 0
        def __call__(self): return self.now
    timer = Timer()
    cache = Cache(timer=timer)
    cache.configure(ttl=3)
    cache.set("x", 9)
    timer.now = 3
    assert not cache.has("x")


def test_lru_touch_controls_eviction():
    cache = LRUCache(maxsize=2)
    cache.set("a", 1); cache.set("b", 2)
    assert cache.get("a") == 1
    cache.set("c", 3)
    assert "a" in cache and "b" not in cache and "c" in cache


def test_required_api_surface():
    from featurelifted import Cache, LRUCache
    assert isinstance(Cache, type)
    assert isinstance(LRUCache, type)
    assert all(callable(getattr(Cache, n)) for n in ('set', 'get', 'delete', 'configure'))


def test_no_upstream_import_surface():
    import re
    from pathlib import Path
    import featurelifted
    pattern = re.compile(r"^\s*(?:from cacheout|import cacheout)\b", re.MULTILINE)
    for path in Path(featurelifted.__file__).parent.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8"))
