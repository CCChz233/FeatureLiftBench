# FeatureLift Task: Humanize natural time and delta formatting

Extract humanize naturaltime/naturaldelta/naturaldate helpers without importing humanize.

## Target API

- Import: `import featurelifted; from featurelifted import naturaltime, naturaldelta, naturaldate, naturalday, precisedelta`
- Callable: `featurelifted.naturaltime`
- Signature: `naturaltime(value, future=False, months=True, minimum_unit='seconds', when=None) -> str`

## Excluded Behavior

- filesize/lists/number formatting beyond time deps
- non-English locale packs
- original humanize import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `humanize`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — naturaltime relative phrasing with when=
- **B002** — naturaldelta month/year granularity
- **B003** — precisedelta suppress and minimum_unit
- **B004** — naturaldate and naturalday phrasing
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: humanize
<!-- featureliftbench:behavior-clauses:end -->
