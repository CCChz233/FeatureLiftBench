from vibe_app.csv_transform.cleaner import filter_by_min_quantity, row_is_valid


def filter_records(rows: list[dict], *, min_quantity: int = 0) -> list[dict]:
    kept: list[dict] = []
    for row in rows:
        if not row_is_valid(row):
            continue
        if min_quantity and not filter_by_min_quantity(row, min_quantity):
            continue
        kept.append(row)
    return kept
