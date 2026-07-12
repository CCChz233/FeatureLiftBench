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
