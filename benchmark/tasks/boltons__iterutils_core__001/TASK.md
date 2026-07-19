# FeatureLift Task: Iterutils iterator toolkit

Extract boltons iterutils chunked/windowed/remap/bucketize helpers without importing boltons.

## Target API

- Import: `import featurelifted; from featurelifted import chunked, windowed, pairwise, unique, bucketize, remap, get_path, partition; from featurelifted.iterutils import backoff, chunk_ranges`
- Callable: `featurelifted.chunked`
- Signature: `chunked(src, size, count=None, **kw) -> list`

## Excluded Behavior

- other boltons utility modules beyond curated snapshot
- upstream docs and packaging
- original boltons import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `boltons`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — chunked and windowed iteration with size validation
- **B002** — pairwise adjacent pairs
- **B003** — unique with optional key function
- **B004** — bucketize grouping with key_filter and value_transform
- **B005** — remap tree walk with visit/enter/exit hooks
- **B006** — get_path nested dict/list access
- **B007** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B008** — the submitted package does not import forbidden upstream packages: boltons
<!-- featureliftbench:behavior-clauses:end -->
