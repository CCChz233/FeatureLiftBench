from __future__ import annotations

from featurelifted import TransformOptions
from featurelifted import transform_csv

SAMPLE_CSV = """SKU,Name,Quantity,Category,Unit_Price
A100,Widget,12,electronics,9.99
B200,Notebook,3,books,4.50
C300,Rice,60,grocery,2.10
D400,Gadget,8,electronics,15.00
"""


def test_transform_normalizes_headers_and_filters_min_quantity() -> None:
    rows = transform_csv(SAMPLE_CSV, options=TransformOptions(min_quantity=5))

    assert [row["sku"] for row in rows] == ["A100", "C300", "D400"]
    assert rows[0]["quantity"] == 12
    assert rows[0]["unit_price"] == 9.99


def test_transform_sorts_by_sku_when_not_grouping() -> None:
    csv_text = "sku,name,quantity,category,unit_price\nz9,Z,6,books,1.0\na1,A,7,books,2.0\n"
    rows = transform_csv(csv_text)

    assert [row["sku"] for row in rows] == ["a1", "z9"]
