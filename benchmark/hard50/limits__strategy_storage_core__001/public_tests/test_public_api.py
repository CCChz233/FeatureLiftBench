from __future__ import annotations

from featurelifted import FixedWindowRateLimiter, MemoryStorage, parse


def test_fixed_window_allows_until_limit() -> None:
    item = parse("2/second")
    limiter = FixedWindowRateLimiter(MemoryStorage())
    assert limiter.hit(item, "user-a") is True
    assert limiter.hit(item, "user-a") is True
    assert limiter.hit(item, "user-a") is False


def test_window_stats_report_zero_remaining_after_exhaustion() -> None:
    item = parse("1/second")
    limiter = FixedWindowRateLimiter(MemoryStorage())
    assert limiter.hit(item, "user-b") is True
    stats = limiter.get_window_stats(item, "user-b")
    assert stats.remaining == 0


def test_distinct_identifiers_have_independent_windows() -> None:
    item = parse("1/second")
    limiter = FixedWindowRateLimiter(MemoryStorage())
    assert limiter.hit(item, "alice") is True
    assert limiter.hit(item, "bob") is True
    assert limiter.hit(item, "alice") is False
    assert limiter.hit(item, "bob") is False


def test_parse_accepts_minute_limit_string() -> None:
    item = parse("5/minute")
    limiter = FixedWindowRateLimiter(MemoryStorage())
    for _ in range(5):
        assert limiter.hit(item, "burst") is True
    assert limiter.hit(item, "burst") is False
