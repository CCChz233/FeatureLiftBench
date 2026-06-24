from __future__ import annotations

from featurelifted import TransformOptions
from featurelifted import transform_csv


def test_dedupe_keeps_last_sku_row() -> None:
    csv_text = (
        "sku,name,quantity,category,unit_price\n"
        "dup,First,2,books,1.0\n"
        "dup,Second,4,books,3.0\n"
        "keep,Other,1,books,2.0\n"
    )
    rows = transform_csv(csv_text)

    assert len(rows) == 2
    dup = next(row for row in rows if row["sku"] == "dup")
    assert dup["name"] == "Second"
    assert dup["quantity"] == 4


def test_group_by_aggregates_quantity_and_price() -> None:
    csv_text = (
        "sku,name,quantity,category,unit_price\n"
        "a1,A,2,electronics,5.0\n"
        "a2,B,3,electronics,7.0\n"
        "b1,C,4,books,1.0\n"
    )
    rows = transform_csv(csv_text, options=TransformOptions(group_by="category"))

    electronics = next(row for row in rows if row["category"] == "electronics")
    assert electronics["quantity"] == 5
    assert electronics["unit_price"] == 12.0
    assert electronics["rows"] == 2


def test_invalid_rows_are_dropped() -> None:
    csv_text = (
        "sku,name,quantity,category,unit_price\n"
        ",Missing,2,books,1.0\n"
        "x1,Zero,0,books,1.0\n"
        "x2,Good,2,books,3.5\n"
    )
    rows = transform_csv(csv_text)

    assert len(rows) == 1
    assert rows[0]["sku"] == "x2"
