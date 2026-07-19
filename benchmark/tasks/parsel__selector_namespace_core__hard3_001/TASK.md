# FeatureLift Task: Selector namespaces

Extract parsel selector namespace behavior into `featurelifted`.

## Target API

```python
from featurelifted import Selector, FakeElement, extract_text
```

## Required Behavior

- `Selector.css` and `Selector.xpath` select nodes from a lightweight element tree.
- `Selector.register_namespace` enables prefixed XPath tag matching.
- `extract_text` joins nested text with sensible defaults.

## Constraints

- Forbidden imports: `parsel`.
- Local element trees only; no lxml/cssselect.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — CSS/XPath subset
- **B002** — namespace registry
- **B003** — text extraction
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: parsel
<!-- featureliftbench:behavior-clauses:end -->
