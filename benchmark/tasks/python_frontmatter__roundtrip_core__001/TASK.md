# FeatureLift Task: YAML front matter round-trip

Extract parse/load/dump of markdown with YAML front matter, preserving body text and metadata across round-trip without importing frontmatter.

## Target API

- Import: `import featurelifted; from featurelifted import Post, parse, load, loads, dump, dumps, checks`
- Callable: `featurelifted.loads`
- Signature: `loads(text, encoding='utf-8', handler=None, **defaults) -> Post`

## Excluded Behavior

- TOML and JSON handler round-trips
- CLI, Sphinx docs, examples, and upstream test suite
- original frontmatter import at runtime
- pyaml pretty-dump integration

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `frontmatter`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — parse and loads YAML front matter delimited by --- lines
- **B002** — dump and dumps serialize Post metadata and markdown body
- **B003** — detect delimiter lines with optional trailing whitespace
- **B004** — normalize CRLF input and merge parse defaults
- **B005** — Post dict-like metadata access and to_dict export
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: frontmatter
<!-- featureliftbench:behavior-clauses:end -->
