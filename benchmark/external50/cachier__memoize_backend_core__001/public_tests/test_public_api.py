from featurelifted import cachier


def test_memory_backend_memoizes_by_arguments():
    calls = []
    @cachier(backend="memory")
    def add(a, b): calls.append((a, b)); return a + b
    assert add(1, 2) == add(1, 2) == 3
    assert add(2, 3) == 5 and calls == [(1, 2), (2, 3)]


def test_skip_and_overwrite_controls():
    calls = []
    @cachier(backend="memory")
    def value(x): calls.append(x); return len(calls)
    assert value(1) == 1 and value(1) == 1
    assert value(1, cachier__skip_cache=True) == 2
    assert value(1) == 1
    assert value(1, cachier__overwrite_cache=True) == 3
    assert value(1) == 3
