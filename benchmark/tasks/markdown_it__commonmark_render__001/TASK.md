# FeatureLift Task: CommonMark block/inline parsing and HTML rendering

Extract markdown-it-py's MarkdownIt parser and renderer for CommonMark-compatible HTML output.

## Target API

- Import: `from featurelifted import MarkdownIt`
- Callable: `featurelifted.MarkdownIt`
- Signature: `MarkdownIt(config='commonmark', options_update=None, renderer_cls=None)`

## Excluded Behavior

- CLI entrypoints
- plugin ecosystem beyond core parser rules
- documentation and benchmark fixtures

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `markdown_it`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — render headings, paragraphs, emphasis, lists, blockquotes, links, images, code spans, and fenced code blocks
- **B002** — escape raw text correctly in rendered HTML
- **B003** — parse Markdown into Token objects with nesting, tags, attrs, content, and markup
- **B004** — support the commonmark preset and enable/disable rules
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: markdown_it
<!-- featureliftbench:behavior-clauses:end -->
