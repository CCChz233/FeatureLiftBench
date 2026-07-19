# FeatureLift Task: CSV transform pipeline

Extract the VibeShop CSV ingest pipeline (normalize, filter, dedupe, optional aggregate) as a standalone package.

## Target API

- Import: `from featurelifted import TransformOptions, transform_csv`
- Callable: `featurelifted.transform_csv`
- Signature: `transform_csv(csv_text: str, *, options: TransformOptions | None = None) -> list[dict]`

## Excluded Behavior

- pricing rules and YAML bootstrap
- HTTP routes and catalog services
- CSV writer serialization helpers for responses
- original project tests and CLI entrypoints

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `vibe_app`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — parse CSV text into row dicts
- **B002** — normalize headers and coerce quantity/unit_price fields
- **B003** — drop invalid rows and enforce minimum quantity
- **B004** — dedupe rows by sku keeping last occurrence
- **B005** — optionally aggregate rows by a grouping key
- **B006** — sort stable output when not aggregating
- **B007** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B008** — the submitted package does not import forbidden upstream packages: vibe_app
<!-- featureliftbench:behavior-clauses:end -->
