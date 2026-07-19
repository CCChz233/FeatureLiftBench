# FeatureLift Task: Phone number parse and format

Extract libphonenumber parse/format for US and GB regions without importing phonenumbers.

## Target API

- Import: `from featurelifted import PhoneNumberFormat, NumberParseException, format_number, is_valid_number, parse; from featurelifted.phonenumberutil import NumberParseException`
- Callable: `featurelifted.parse`
- Signature: `parse(number: str, region: str | None = None) -> PhoneNumber`

## Excluded Behavior

- full global geodata/carrier/timezone datasets
- PhoneNumberMatcher and short-number data
- original phonenumbers import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `phonenumbers`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — parse E.164 and national numbers for US and GB
- **B002** — format NATIONAL, INTERNATIONAL, and E164
- **B003** — validate numbers against region metadata
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: phonenumbers
<!-- featureliftbench:behavior-clauses:end -->
