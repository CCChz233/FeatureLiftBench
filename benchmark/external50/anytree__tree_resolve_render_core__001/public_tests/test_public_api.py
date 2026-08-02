from __future__ import annotations

from featurelifted import (
    ChildResolverError,
    Node,
    PreOrderIter,
    RenderTree,
    Resolver,
    findall,
)


def test_build_and_preorder() -> None:
    root = Node("udo")
    marc = Node("marc", parent=root)
    Node("lian", parent=marc)
    assert [n.name for n in PreOrderIter(root)] == ["udo", "marc", "lian"]


def test_resolver_get() -> None:
    root = Node("udo")
    marc = Node("marc", parent=root)
    lian = Node("lian", parent=marc)
    r = Resolver("name")
    assert r.get(root, "/udo/marc/lian") is lian
    try:
        r.get(root, "/udo/missing")
        assert False, "expected ChildResolverError"
    except ChildResolverError:
        pass


def test_render_and_findall() -> None:
    root = Node("udo")
    Node("marc", parent=root)
    lines = [f"{row.pre}{row.node.name}" for row in RenderTree(root)]
    assert lines[0] == "udo"
    assert any("marc" in line for line in lines)
    found = findall(root, filter_=lambda n: n.name.startswith("m"))
    assert [n.name for n in found] == ["marc"]
