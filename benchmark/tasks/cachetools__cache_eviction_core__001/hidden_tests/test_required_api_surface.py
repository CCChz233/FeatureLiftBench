"""Constitution API-surface coverage generated from public_spec."""

from featurelifted import (
    LRUCache,
    TTLCache,
    LFUCache,
    cached,
    hashkey,
    typedkey,
)


def test_required_api_surface():
    assert isinstance(LRUCache, type)
    assert LRUCache is not None
    assert isinstance(TTLCache, type)
    assert isinstance(LFUCache, type)
    assert callable(cached)
    assert callable(hashkey)
    assert callable(typedkey)
