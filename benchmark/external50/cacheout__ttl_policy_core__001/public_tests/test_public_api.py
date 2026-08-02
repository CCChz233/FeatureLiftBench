from featurelifted import Cache, LRUCache


class Timer:
    def __init__(self): self.now = 0
    def __call__(self): return self.now


def test_cache_roundtrip_and_delete():
    cache = Cache(maxsize=2)
    cache.set("a", 1)
    assert cache.get("a") == 1
    assert cache.delete("a") == 1
    assert cache.get("a") is None


def test_ttl_uses_injected_timer():
    timer = Timer()
    cache = Cache(ttl=2, timer=timer)
    cache.set("a", 1)
    timer.now = 1
    assert cache.get("a") == 1
    timer.now = 2
    assert cache.get("a") is None
