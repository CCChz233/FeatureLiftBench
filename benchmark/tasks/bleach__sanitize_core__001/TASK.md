# FeatureLift Task: HTML sanitizer clean core

Extract bleach clean/Cleaner HTML sanitization without importing bleach.

## Target API

- Import: `import featurelifted; from featurelifted import clean, Cleaner, ALLOWED_TAGS, ALLOWED_ATTRIBUTES, ALLOWED_PROTOCOLS`
- Callable: `featurelifted.clean`
- Signature: `clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, styles=ALLOWED_STYLES, protocols=ALLOWED_PROTOCOLS, strip=False, strip_comments=True) -> str`

## Excluded Behavior

- linkify
- upstream packaging
- original bleach import

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `bleach`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — XSS tag stripping
- **B002** — allowed attributes and protocols
- **B003** — strip and strip_comments modes
- **B004** — callable attribute filters
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: bleach
<!-- featureliftbench:behavior-clauses:end -->
