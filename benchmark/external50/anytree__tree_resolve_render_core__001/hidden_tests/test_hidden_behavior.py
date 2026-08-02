from __future__ import annotations

import re
from pathlib import Path

from featurelifted import (
    Node,
    PreOrderIter,
    RenderTree,
    Resolver,
    ResolverError,
    findall,
)


def test_parent_children_mutation() -> None:
    root = Node("r")
    a = Node("a")
    a.parent = root
    assert a in root.children
    assert list(PreOrderIter(root))[1] is a


def test_resolver_relative_path() -> None:
    root = Node("r")
    a = Node("a", parent=root)
    b = Node("b", parent=a)
    r = Resolver("name")
    assert r.get(a, "b") is b


def test_render_row_fields() -> None:
    root = Node("r")
    Node("c", parent=root)
    rows = list(RenderTree(root))
    assert hasattr(rows[0], "pre") and hasattr(rows[0], "fill") and hasattr(rows[0], "node")


def test_findall_empty() -> None:
    root = Node("r")
    assert findall(root, filter_=lambda n: False) == ()


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\s*(?:from anytree\b|import anytree\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path


def test_resolver_error_base() -> None:
    assert issubclass(ResolverError, Exception)
