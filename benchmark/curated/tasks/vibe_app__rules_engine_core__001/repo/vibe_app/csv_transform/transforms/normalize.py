from vibe_app.csv_transform.mapper import coerce_numeric_fields, normalize_row_keys


def normalize_record(row: dict) -> dict:
    return coerce_numeric_fields(normalize_row_keys(row))
