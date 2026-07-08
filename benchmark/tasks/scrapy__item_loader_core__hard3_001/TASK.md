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
