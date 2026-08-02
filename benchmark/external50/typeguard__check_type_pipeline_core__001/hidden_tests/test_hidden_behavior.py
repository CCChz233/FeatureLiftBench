from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from featurelifted import CollectionCheckStrategy, TypeCheckError, check_type


def test_dict_nested_list() -> None:
    value = {"nums": [1, 2]}
    assert check_type(value, dict[str, list[int]]) == value


def test_first_item_strategy_can_miss() -> None:
    first = CollectionCheckStrategy["FIRST_ITEM"]
    all_items = CollectionCheckStrategy["ALL_ITEMS"]
    # FIRST_ITEM may accept heterogeneous lists that ALL_ITEMS rejects
    check_type([1, "x"], list[int], collection_check_strategy=first)
    try:
        check_type([1, "x"], list[int], collection_check_strategy=all_items)
        assert False
    except TypeCheckError:
        pass


def test_optional_reject() -> None:
    try:
        check_type("x", Optional[int])
        assert False
    except TypeCheckError:
        pass


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\s*(?:from typeguard\b|import typeguard\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
