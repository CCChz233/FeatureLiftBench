from featurelifted import retry, retry_context


def test_retry_decorator_succeeds_after_failures():
    calls = []
    @retry(on=ValueError, attempts=3, timeout=None, wait_initial=0, wait_max=0, wait_jitter=0)
    def work():
        calls.append(1)
        if len(calls) < 3: raise ValueError("again")
        return "ok"
    assert work() == "ok" and len(calls) == 3


def test_retry_context_attempt_numbers():
    seen = []
    for attempt in retry_context(on=ValueError, attempts=3, timeout=None, wait_initial=0, wait_max=0, wait_jitter=0):
        with attempt:
            seen.append(attempt.num)
            if attempt.num < 3: raise ValueError("again")
    assert seen == [1, 2, 3]
