# FeatureLift Task: Language-tag normalization and CLDR metadata

Extract language tag normalization, name lookup, likely-subtag expansion, and distance matching with offline CLDR data.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    best_match,
    Language,
    standardize_tag,
)
```

## Required API Details

- `Language` class must be importable
  - `Language.get(tag, normalize=True) -> Language`
  - `Language.to_tag() -> str`
  - `Language.language_name(language=None) -> str`
  - `Language.maximize() -> Language`
  - `Language.script` attribute must exist on instances
- `standardize_tag(tag, macro: bool = False) -> str`
- `best_match(desired_language, supported_languages, min_score=0) -> tuple[str, int]`

## Required Behavior

- standardize_tag and Language.get normalize overlong, deprecated, script, and territory subtags.
- language_name and maximize resolve localized CLDR metadata from the locked language-data package offline.
- best_match ranks supported language tags using normalized language distance and returns a score.
- The submitted package uses only locked language-data and marisa-trie dependencies and does not import langcodes.

## Constraints

- Forbidden imports: `langcodes`.
- Do not implement data rebuild scripts.
- Do not implement online registry updates.
- Do not implement population statistics beyond the declared API.
- Do not implement original langcodes import at runtime.

## Public vs Hidden Tests

Public tests cover common use. Hidden tests cover documented edge, configuration, state, API-surface, and isolation behavior only.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — standardize_tag and Language.get normalize overlong, deprecated, script, and territory subtags.
- **B002** — language_name and maximize resolve localized CLDR metadata from the locked language-data package offline.
- **B003** — best_match ranks supported language tags using normalized language distance and returns a score.
- **B004** — The submitted package uses only locked language-data and marisa-trie dependencies and does not import langcodes.
<!-- featureliftbench:behavior-clauses:end -->
