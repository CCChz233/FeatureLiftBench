from featurelifted import cachier, disable_caching, enable_caching


def test_clear_and_precache_methods():
    calls = []
    @cachier(backend="memory")
    def value(x): calls.append(x); return x * 2
    value.precache_value(3, value_to_cache=7)
    assert value(3) == 7 and calls == []
    value.clear_cache()
    assert value(3) == 6 and calls == [3]


def test_overwrite_replaces_existing_entry():
    calls = []
    @cachier(backend="memory")
    def value(): calls.append(1); return len(calls)
    assert value() == 1 and value() == 1
    assert value(cachier__overwrite_cache=True) == 2
    assert value() == 2


def test_global_disable_bypasses_cache():
    calls = []
    @cachier(backend="memory")
    def value(): calls.append(1); return len(calls)
    try:
        disable_caching()
        assert (value(), value()) == (1, 2)
    finally:
        enable_caching()


def test_required_api_surface():
    from featurelifted import cachier, disable_caching, enable_caching, get_default_params, set_default_params
    assert all(callable(x) for x in (cachier, set_default_params, get_default_params, enable_caching, disable_caching))


def test_no_upstream_import_surface():
    import re
    from pathlib import Path
    import featurelifted
    pattern = re.compile(r"^\s*(?:from cachier|import cachier)\b", re.MULTILINE)
    for path in Path(featurelifted.__file__).parent.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8"))
