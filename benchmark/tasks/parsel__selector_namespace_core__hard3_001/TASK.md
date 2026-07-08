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
