# FeatureLift Task: Markdown tables and footnotes extensions

Extract python-markdown core with tables and footnotes extensions.

## Target API

- Import: `import featurelifted; from featurelifted import markdown, Markdown`
- Callable: `featurelifted.markdown`
- Signature: `markdown(text, extensions=None, extension_configs=None) -> str`

## Excluded Behavior

- unrelated extensions
- CLI __main__
- original markdown import

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `markdown`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — pipe table rendering
- **B002** — footnote reference and backlink HTML
- **B003** — extension registration on Markdown class
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: markdown
<!-- featureliftbench:behavior-clauses:end -->
