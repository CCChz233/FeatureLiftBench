"""CSV reader stage."""

from __future__ import annotations

import csv
import io
from typing import Any


def read_csv_rows(text: str) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(text))
    return [dict(row) for row in reader]
