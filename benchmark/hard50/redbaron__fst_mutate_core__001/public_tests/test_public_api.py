from __future__ import annotations

from featurelifted import RedBaron


def test_dumps_roundtrip() -> None:
    source = "def foo():\n    return 1\n"
    tree = RedBaron(source)
    assert tree.dumps() == source


def test_rename_function_preserves_body() -> None:
    source = "def foo():\n    return 1\n"
    tree = RedBaron(source)
    node = tree.find("def", name="foo")
    node.name = "bar"
    assert tree.dumps() == "def bar():\n    return 1\n"
