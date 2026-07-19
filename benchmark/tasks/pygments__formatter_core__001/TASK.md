# FeatureLift Task: HTML formatter core

Extract Pygments HTML syntax highlighting formatter and highlight() integration with lexers as a standalone package.

## Target API

- Import: `from featurelifted import highlight, HtmlFormatter, get_lexer_by_name`
- Callable: `featurelifted.highlight`
- Signature: `highlight(code: str, lexer: Lexer, formatter: Formatter, outfile: IO[str] | None = None) -> str`

## Excluded Behavior

- image, LaTeX, RTF, SVG, and terminal formatters
- command-line pygmentize tool
- full lexer catalog beyond Python integration
- original project tests and documentation

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `pygments`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — render token streams to HTML spans with HtmlFormatter
- **B002** — highlight source with highlight(code, lexer, formatter)
- **B003** — support nowrap, linenos, cssclass, and title options
- **B004** — escape HTML in source text and preserve token class names
- **B005** — resolve Python lexer for integrated highlighting
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: pygments
<!-- featureliftbench:behavior-clauses:end -->
