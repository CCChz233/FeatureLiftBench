# FeatureLift Task: version_from_scm

Extract setuptools_scm version normalization into `featurelifted`.

## Target API

```python
from featurelifted import version_from_scm
```

## Required Behavior

- `version_from_scm` normalizes tag names, distance-from-tag dev suffixes, and local node suffixes.
- Dirty trees and positive distance append local version segments.

## Constraints

- Forbidden imports: `setuptools_scm`.
- Use fake SCM inputs; no subprocess git.
