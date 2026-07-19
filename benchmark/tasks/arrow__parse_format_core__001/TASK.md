# FeatureLift Task: Arrow parse, format, and humanize subset

Extract Arrow parsing, strftime-style formatting, and English humanize without importing arrow.

## Target API

- Import: `import featurelifted; from featurelifted import Arrow, get`
- Callable: `featurelifted.get`
- Signature: `get(*args, **kwargs) -> Arrow`

## Excluded Behavior

- 60+ locale packs beyond English
- timezone name database beyond utc/fixed offsets
- factory range/span utilities and CLI
- original arrow import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `arrow`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — parse ISO and format-string datetimes
- **B002** — format with token literals in brackets
- **B003** — humanize relative deltas in English
- **B004** — ordinal Do token parsing
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: arrow
<!-- featureliftbench:behavior-clauses:end -->
