# FeatureLift Task: CLDR plural rules subset

Extract Babel plural rule parsing and locale plural_form selection backed by CLDR locale-data files.

## Target API

- Import: `from featurelifted import PluralRule, Locale`
- Callable: `featurelifted.Locale.parse`
- Signature: `Locale.parse(identifier: str) -> Locale`

## Excluded Behavior

- gettext message catalogs and extraction
- number/date/currency formatting modules
- full CLDR locale-data tree

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `babel`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — evaluate PluralRule expressions for numeric operands
- **B002** — resolve Locale plural categories for en, ru, fr, ja, and pl
- **B003** — load plural rules from packaged locale-data .dat resources
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: babel
<!-- featureliftbench:behavior-clauses:end -->
