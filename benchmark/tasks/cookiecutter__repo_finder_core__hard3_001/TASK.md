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

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — abbreviation expansion
- **B002** — replay override
- **B003** — safe path join
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: cookiecutter
<!-- featureliftbench:behavior-clauses:end -->
