import sys
from featurelifted import AttachInfo, Scanner, attach, lift


def test_attach_returns_info_and_preserves_object():
    def target(): return 3
    original = target
    info = attach(target, lambda *args: None, category="x", depth=0)
    assert target is original and isinstance(info, AttachInfo)


def test_callback_order_with_same_category():
    seen = []
    def target(): pass
    target.__module__ = __name__; globals()["_flb_order_target"] = target
    attach(target, lambda *args: seen.append(1), category="x", depth=0)
    attach(target, lambda *args: seen.append(2), category="x", depth=0)
    try:
        Scanner().scan(sys.modules[__name__], categories=("x",))
        assert seen == [1, 2]
        assert isinstance(lift, type)
    finally:
        globals().pop("_flb_order_target", None)


def test_required_api_surface():
    from featurelifted import AttachInfo, Scanner, attach, lift
    assert callable(attach)
    assert isinstance(Scanner, type) and callable(Scanner.scan)
    assert isinstance(AttachInfo, type) and isinstance(lift, type)


def test_no_upstream_import_surface():
    import re
    from pathlib import Path
    import featurelifted
    pattern = re.compile(r"^\s*(?:from venusian|import venusian)\b", re.MULTILINE)
    for path in Path(featurelifted.__file__).parent.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8"))
