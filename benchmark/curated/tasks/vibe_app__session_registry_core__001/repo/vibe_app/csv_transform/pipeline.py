"""CSV transform pipeline orchestrator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from vibe_app.csv_transform.reader import read_csv_rows
from vibe_app.csv_transform.transforms import (
    aggregate_by,
    dedupe_by_sku,
    filter_records,
    normalize_record,
)
from vibe_app.state import GLOBAL_STATE


@dataclass
class TransformOptions:
    group_by: str | None = None
    min_quantity: int = 0
    dedupe: bool = True


def transform_csv(csv_text: str, *, options: TransformOptions | None = None) -> list[dict[str, Any]]:
    opts = options or TransformOptions()
    rows = read_csv_rows(csv_text)
    normalized = [normalize_record(row) for row in rows]
    filtered = filter_records(normalized, min_quantity=opts.min_quantity)
    if opts.dedupe:
        filtered = dedupe_by_sku(filtered)
    if opts.group_by:
        filtered = aggregate_by(filtered, opts.group_by)
    else:
        filtered = sorted(filtered, key=lambda row: str(row.get("sku", "")))
    GLOBAL_STATE["last_csv_job"] = {"rows": len(filtered), "group_by": opts.group_by}
    return filtered
