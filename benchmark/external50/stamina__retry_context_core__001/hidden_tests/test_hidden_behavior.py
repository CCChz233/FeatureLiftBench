import pytest
from featurelifted import retry, set_active, set_testing


def test_unconfigured_exception_is_not_retried():
    calls = []
    @retry(on=ValueError, attempts=3, timeout=None, wait_initial=0, wait_max=0, wait_jitter=0)
    def work(): calls.append(1); raise TypeError("stop")
    with pytest.raises(TypeError): work()
    assert len(calls) == 1


def test_retry_context_stops_after_success():
    from featurelifted import retry_context
    seen = []
    for attempt in retry_context(on=ValueError, attempts=4, timeout=None, wait_initial=0, wait_max=0, wait_jitter=0):
        with attempt:
            seen.append(attempt.num)
            if attempt.num == 1: raise ValueError("again")
    assert seen == [1, 2]


def test_inactive_policy_calls_once():
    calls = []
    set_active(False)
    try:
        @retry(on=ValueError, attempts=3, timeout=None, wait_initial=0, wait_max=0, wait_jitter=0)
        def work(): calls.append(1); raise ValueError("stop")
        with pytest.raises(ValueError): work()
        assert len(calls) == 1
    finally:
        set_active(True); set_testing(False)


def test_required_api_surface():
    from featurelifted import Attempt, retry, retry_context, set_active, set_testing
    assert all(callable(x) for x in (retry, retry_context, set_active, set_testing))
    assert isinstance(Attempt, type)


def test_no_upstream_import_surface():
    import re
    from pathlib import Path
    import featurelifted
    pattern = re.compile(r"^\s*(?:from stamina|import stamina)\b", re.MULTILINE)
    for path in Path(featurelifted.__file__).parent.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8"))
