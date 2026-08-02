import pytest
from featurelifted import EventEmitter, PyeeError


def test_remove_listener_changes_dispatch():
    emitter = EventEmitter(); seen = []
    def listener(): seen.append(1)
    emitter.on("x", listener); emitter.remove_listener("x", listener)
    assert emitter.emit("x") is False and seen == []


def test_unhandled_error_semantics():
    emitter = EventEmitter()
    with pytest.raises(ValueError): emitter.emit("error", ValueError("bad"))
    with pytest.raises(PyeeError): emitter.emit("error", "bad")


def test_required_api_surface():
    from featurelifted import EventEmitter, PyeeError
    assert isinstance(EventEmitter, type)
    assert issubclass(PyeeError, Exception)
    assert all(callable(getattr(EventEmitter, n)) for n in ('on', 'once', 'emit', 'remove_listener', 'remove_all_listeners', 'listeners'))


def test_no_upstream_import_surface():
    import re
    from pathlib import Path
    import featurelifted
    pattern = re.compile(r"^\s*(?:from pyee|import pyee)\b", re.MULTILINE)
    for path in Path(featurelifted.__file__).parent.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8"))
