# FeatureLift Task: Console markup parsing

Extract Rich console markup rendering into Text spans, including escaping, nested styles, links, and error handling.

## Target API

- Import: `from featurelifted.markup import render, escape; from featurelifted.text import Text; from featurelifted.errors import MarkupError`
- Callable: `featurelifted.markup.render`
- Signature: `render(markup: str, style: str | Style = '', emoji: bool = True) -> Text`

## Excluded Behavior

- full Console rendering pipeline and terminal detection
- progress bars, tables, and layout renderables
- syntax highlighting and live displays

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `rich`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — render markup tags into Text with style spans
- **B002** — escape square brackets for literal markup
- **B003** — support nested/open/close tags and link metadata
- **B004** — raise MarkupError on mismatched closing tags
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: rich
<!-- featureliftbench:behavior-clauses:end -->
