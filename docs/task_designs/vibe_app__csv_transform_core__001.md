# Task Design: vibe_app__csv_transform_core__001

Status: oracle-verified

## Why This Task

Extract a multi-stage CSV ingest pipeline spread across reader/mapper/cleaner/transform modules with duplicate string helpers and global job metadata side effects.

## Source

| Field | Value |
| --- | --- |
| Source repo | `sources/vibe_app/` |
| Commit | curated |
| License | MIT |
| Language | Python |
| Difficulty | hard |
| Tags | extreme, multi-task-repo, functional-discriminator, legacy_vibe_clutter |

## Target Feature

### Source entrypoints

- `vibe_app.csv_transform.transform_csv`
- `vibe_app.csv_transform.pipeline.TransformOptions`

### Output API

```python
from featurelifted import TransformOptions, transform_csv
```

## Public Tests

- Normalize headers, coerce numerics, filter by minimum quantity.
- Stable sku sort when not grouping.

## Hidden Tests

- Dedupe keeps last row per sku.
- Optional `group_by` aggregates quantity and unit_price sums.
- Invalid/zero-quantity rows are dropped.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Dedupe stage | `transforms/dedupe.py` | `test_dedupe_keeps_last_sku_row` |
| Aggregate stage | `transforms/aggregate.py` | `test_group_by_aggregates_quantity_and_price` |
| Row validation | `cleaner.py` | `test_invalid_rows_are_dropped` |

## Manual Oracle Closure Plan

Expected closure shape:

```text
featurelifted/
  __init__.py
  state.py
  helpers/strings.py
  csv_transform/
    pipeline.py
    reader.py
    mapper.py
    cleaner.py
    transforms/
      normalize.py
      filter_rows.py
      aggregate.py
      dedupe.py
```
