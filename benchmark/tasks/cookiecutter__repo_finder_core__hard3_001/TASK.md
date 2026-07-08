# FeatureLift Task: RepoFinder

Extract cookiecutter repository finder into `featurelifted`.

## Target API

```python
from featurelifted import RepoFinder, expand_abbreviation, safe_join
```

## Required Behavior

- `RepoFinder.find_template` resolves repository specs to local template paths.
- Abbreviations expand short repo prefixes; replay overrides take precedence.
- `safe_join` rejects path traversal and absolute segments.
- Nested templates are detected from path structure.

## Constraints

- Forbidden imports: `cookiecutter`.
- No git or network access.
