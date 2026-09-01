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

- Constructing `PublicSuffixList()` without a source loads bundled suffix metadata offline and resolves domains using that data.
- For a domain covered by the loaded rules, `publicsuffix` returns its public suffix, `privatesuffix` returns the registrable private suffix, and `is_public` and `is_private` classify those respective forms.
- When constructed from custom rule text, `publicsuffix` applies wildcard rules and their exception rules to the supplied domain.
- With `accept_unknown=False`, `publicsuffix` returns `None` for a domain whose suffix is absent from the loaded rules.
- The package exposes the required task API paths `featurelifted.PublicSuffixList`, `featurelifted.PublicSuffixList.publicsuffix`, `featurelifted.PublicSuffixList.privatesuffix`, `featurelifted.PublicSuffixList.is_public`, and `featurelifted.PublicSuffixList.is_private` with the kinds and callable signatures listed in this contract.
- the submitted package does not import forbidden upstream packages: publicsuffixlist.

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

- **B001** — Constructing `PublicSuffixList()` without a source loads bundled suffix metadata offline and resolves domains using that data.
- **B002** — For a domain covered by the loaded rules, `publicsuffix` returns its public suffix, `privatesuffix` returns the registrable private suffix, and `is_public` and `is_private` classify those respective forms.
- **B003** — When constructed from custom rule text, `publicsuffix` applies wildcard rules and their exception rules to the supplied domain.
- **B004** — With `accept_unknown=False`, `publicsuffix` returns `None` for a domain whose suffix is absent from the loaded rules.
- **B005** — The package exposes the required task API paths `featurelifted.PublicSuffixList`, `featurelifted.PublicSuffixList.publicsuffix`, `featurelifted.PublicSuffixList.privatesuffix`, `featurelifted.PublicSuffixList.is_public`, and `featurelifted.PublicSuffixList.is_private` with the kinds and callable signatures listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: publicsuffixlist.
<!-- featureliftbench:behavior-clauses:end -->
