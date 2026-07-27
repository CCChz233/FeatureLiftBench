"""String helpers duplicated elsewhere."""

from __future__ import annotations


def slugify(value: str) -> str:
    return "-".join(part for part in value.lower().replace("_", " ").split() if part)


def normalize_header(value: str) -> str:
    return value.strip().lower().replace(" ", "_")
