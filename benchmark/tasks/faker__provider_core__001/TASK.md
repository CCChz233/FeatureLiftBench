# FeatureLift Task: Single-locale Faker providers

Extract Faker factory and Generator wiring for en_US person, address, and phone_number providers with embedded locale data.

## Target API

- Import: `from featurelifted import Faker`
- Callable: `featurelifted.Faker`
- Signature: `Faker(locale: str = 'en_US', providers: list[str] | None = None, **config)`

## Excluded Behavior

- multi-locale weighting and proxy locale switching
- CLI, pytest plugin, and documentation
- providers beyond person, address, and phone_number

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `faker`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — construct Faker with locale en_US and default person/address/phone providers
- **B002** — generate deterministic fake names, addresses, and phone numbers with seed_instance
- **B003** — resolve localized provider modules and locale resource data
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: faker
<!-- featureliftbench:behavior-clauses:end -->
