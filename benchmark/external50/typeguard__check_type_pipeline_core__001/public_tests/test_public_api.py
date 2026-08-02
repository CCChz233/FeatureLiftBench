from __future__ import annotations

from typing import Optional, Union

from featurelifted import CollectionCheckStrategy, TypeCheckError, check_type


def test_nested_collections() -> None:
    assert check_type([1, 2], list[int]) == [1, 2]
    assert check_type({"a": 1}, dict[str, int]) == {"a": 1}


def test_optional_union() -> None:
    assert check_type(None, Optional[int]) is None
    assert check_type(1, Union[int, str]) == 1


def test_type_check_error() -> None:
    all_items = CollectionCheckStrategy["ALL_ITEMS"]
    try:
        check_type([1, "a"], list[int], collection_check_strategy=all_items)
        assert False, "expected TypeCheckError"
    except TypeCheckError:
        pass


def test_collection_strategy() -> None:
    all_items = CollectionCheckStrategy["ALL_ITEMS"]
    assert (
        check_type(
            (1, 2, 3),
            tuple[int, ...],
            collection_check_strategy=all_items,
        )
        == (1, 2, 3)
    )
