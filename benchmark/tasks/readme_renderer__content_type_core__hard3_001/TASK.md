# FeatureLift Task: render_readme

Extract readme_renderer content-type selection into `featurelifted`.

## Target API

```python
from featurelifted import render_readme
```

## Required Behavior

- `render_readme(content, content_type)` selects plain, markdown, or reST renderers.
- Unknown media types fall back to plain text with warnings.
- Unsupported charset parameters produce warnings.

## Constraints

- Forbidden imports: `readme_renderer`.
- No network access.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — content-type parsing
- **B002** — renderer selection
- **B003** — warning capture
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: readme_renderer
<!-- featureliftbench:behavior-clauses:end -->
