# FeatureLift Task: CSV transform pipeline

Extract a task-scoped subset of `vibe_app` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    transform_csv,
    TransformOptions,
)
```

## Required API Details

- `TransformOptions(group_by: 'str | None' = None, min_quantity: 'int' = 0, dedupe: 'bool' = True) -> None` class constructor
- `transform_csv(csv_text: 'str', *, options: 'TransformOptions | None' = None) -> 'list[dict[str, Any]]'`

## Required Behavior

- The extracted feature must support this observable behavior: parse CSV text into row dicts. Required observable cases include invalid rows are dropped.
- The extracted feature must support this observable behavior: normalize headers and coerce quantity/unit_price fields. Required observable cases include transform normalizes headers and filters min quantity; group by aggregates quantity and price.
- The extracted feature must support this observable behavior: drop invalid rows and enforce minimum quantity. Required observable cases include invalid rows are dropped.
- The extracted feature must support this observable behavior: dedupe rows by sku keeping last occurrence. Required observable cases include dedupe keeps last sku row.
- The extracted feature must support this observable behavior: optionally aggregate rows by a grouping key. Required observable cases include group by aggregates quantity and price.
- The extracted feature must support this observable behavior: sort stable output when not aggregating. Required observable cases include transform sorts by sku when not grouping; invalid rows are dropped.
- The package exposes the required task API paths `featurelifted.TransformOptions`, `featurelifted.transform_csv` with the kinds and callable signatures listed in this contract.

## Constraints

- Forbidden imports: `vibe_app`.
- Do not implement pricing rules and YAML bootstrap.
- Do not implement HTTP routes and catalog services.
- Do not implement CSV writer serialization helpers for responses.
- Do not implement original project tests and CLI entrypoints.

## Public vs Hidden Tests

Benchmark evaluator tests remain private. Each evaluator test maps to the public behaviors above and only deepens examples, boundaries, or combinations within those declared behaviors.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: parse CSV text into row dicts. Required observable cases include invalid rows are dropped.
- **B002** — The extracted feature must support this observable behavior: normalize headers and coerce quantity/unit_price fields. Required observable cases include transform normalizes headers and filters min quantity; group by aggregates quantity and price.
- **B003** — The extracted feature must support this observable behavior: drop invalid rows and enforce minimum quantity. Required observable cases include invalid rows are dropped.
- **B004** — The extracted feature must support this observable behavior: dedupe rows by sku keeping last occurrence. Required observable cases include dedupe keeps last sku row.
- **B005** — The extracted feature must support this observable behavior: optionally aggregate rows by a grouping key. Required observable cases include group by aggregates quantity and price.
- **B006** — The extracted feature must support this observable behavior: sort stable output when not aggregating. Required observable cases include transform sorts by sku when not grouping; invalid rows are dropped.
- **B007** — The package exposes the required task API paths `featurelifted.TransformOptions`, `featurelifted.transform_csv` with the kinds and callable signatures listed in this contract.
- **B008** — the submitted package does not import forbidden upstream packages: vibe_app.
<!-- featureliftbench:behavior-clauses:end -->
