import sys
from featurelifted import Scanner, attach


def test_attach_and_scan_current_module():
    seen = []
    def target(): return 1
    target.__module__ = __name__
    globals()["_flb_target"] = target
    attach(target, lambda scanner, name, obj: seen.append((scanner.token, name, obj)), category="jobs", depth=0)
    try:
        Scanner(token=7).scan(sys.modules[__name__])
        assert seen == [(7, "_flb_target", target)]
    finally:
        globals().pop("_flb_target", None)


def test_category_filtering():
    seen = []
    def target(): pass
    target.__module__ = __name__; globals()["_flb_category_target"] = target
    attach(target, lambda *args: seen.append("a"), category="a", depth=0)
    attach(target, lambda *args: seen.append("b"), category="b", depth=0)
    try:
        Scanner().scan(sys.modules[__name__], categories=("b",))
        assert seen == ["b"]
    finally:
        globals().pop("_flb_category_target", None)
