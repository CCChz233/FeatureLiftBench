# FeatureLift Task: Bundled public-suffix metadata lookup

Extract offline PublicSuffixList loading and suffix/domain classification from the bundled PSL snapshot.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    PublicSuffixList,
)
```

## Required API Details

- `PublicSuffixList(source=None, accept_unknown=True, accept_encoded_idn=True, only_icann=False)` class constructor
  - `PublicSuffixList.publicsuffix(domain, accept_unknown=None, keep_case=False)`
  - `PublicSuffixList.privatesuffix(domain, accept_unknown=None, keep_case=False)`
  - `PublicSuffixList.is_public(domain) -> bool`
  - `PublicSuffixList.is_private(domain) -> bool`

## Required Behavior

- PublicSuffixList with no source loads the bundled public_suffix_list.dat resource offline.
- publicsuffix and privatesuffix apply exact, wildcard, and exception rules to normalized domain names.
- only_icann and unknown-suffix options alter classification according to their constructor settings.
- The submitted package does not import publicsuffixlist or perform network refreshes.

## Constraints

- Forbidden imports: `publicsuffixlist`.
- Do not implement updatePSL network refresh.
- Do not implement command-line updates.
- Do not implement live publicsuffix.org access.
- Do not implement original publicsuffixlist import at runtime.

## Public vs Hidden Tests

Public tests cover common use. Hidden tests cover documented edge, configuration, state, API-surface, and isolation behavior only.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — PublicSuffixList with no source loads the bundled public_suffix_list.dat resource offline.
- **B002** — publicsuffix and privatesuffix apply exact, wildcard, and exception rules to normalized domain names.
- **B003** — only_icann and unknown-suffix options alter classification according to their constructor settings.
- **B004** — The submitted package does not import publicsuffixlist or perform network refreshes.
<!-- featureliftbench:behavior-clauses:end -->
