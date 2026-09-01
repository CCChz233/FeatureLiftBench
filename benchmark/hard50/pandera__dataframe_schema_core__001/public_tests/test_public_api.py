from __future__ import annotations

import os

os.environ.setdefault("DISABLE_PANDERA_IMPORT_WARNING", "True")

import pandas as pd
import pytest
from featurelifted import Check, Column, DataFrameSchema
from featurelifted.errors import SchemaError


def _schema() -> DataFrameSchema:
    return DataFrameSchema(
        {
            "age": Column("int64", checks=Check.ge(0), coerce=True),
            "name": Column(str),
        }
    )


def test_validate_matching_dtypes() -> None:
    frame = pd.DataFrame({"age": [1, 2], "name": ["Ada", "Lin"]})
    out = _schema().validate(frame)
    assert list(out.columns) == ["age", "name"]
    assert list(out["name"]) == ["Ada", "Lin"]


def test_coerce_string_to_int() -> None:
    frame = pd.DataFrame({"age": ["3", "4"], "name": ["Ada", "Lin"]})
    out = _schema().validate(frame)
    assert list(out["age"]) == [3, 4]
    assert str(out["age"].dtype).startswith("int")


def test_check_ge_rejects_low_values() -> None:
    frame = pd.DataFrame({"age": [-1], "name": ["Ada"]})
    with pytest.raises(SchemaError):
        _schema().validate(frame)
