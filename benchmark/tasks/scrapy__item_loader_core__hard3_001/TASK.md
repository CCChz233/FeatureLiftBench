# FeatureLift Task: Item loader processor registry

Extract a Scrapy ItemLoader subset into `featurelifted`.

## Target API

```python
from featurelifted import Item, Field, ItemLoader, Compose, TakeFirst, Identity
```

## Required Behavior

- `Item` declares `Field` metadata with optional `input_processor` and `output_processor`.
- `ItemLoader.add_value` applies input processors; `load_item` applies output processors.
- Nested loaders inherit parent default processors.
- Unknown fields raise `KeyError`.

## Constraints

- Forbidden imports: `scrapy`.
- No selector/response/downloader code.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — Item/Field metadata
- **B002** — ItemLoader processor pipeline
- **B003** — nested loaders
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: scrapy
<!-- featureliftbench:behavior-clauses:end -->
