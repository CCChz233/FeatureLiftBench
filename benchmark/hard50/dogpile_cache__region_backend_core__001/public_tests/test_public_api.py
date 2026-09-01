from __future__ import annotations

from featurelifted import CacheRegion, NO_VALUE, make_region


def test_make_configure_and_get_or_create() -> None:
    region = make_region(name="primary")
    assert isinstance(region, CacheRegion)
    assert region.name == "primary"
    assert region.is_configured is False
    assert region.configure("dogpile.cache.memory") is region
    assert region.is_configured is True

    calls: list[str] = []

    def creator() -> str:
        calls.append("called")
        return "value"

    assert region.get_or_create("key", creator) == "value"
    assert region.get_or_create("key", lambda: "replacement") == "value"
    assert calls == ["called"]


def test_missing_key_returns_no_value() -> None:
    region = make_region().configure("dogpile.cache.memory")
    assert region.get("missing") is NO_VALUE
    assert not NO_VALUE
