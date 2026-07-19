# FeatureLift Task: Jinja2 lexer and parser core

Extract Jinja2 template lexing and parsing into AST nodes as a standalone package.

## Target API

- Import: `from featurelifted import Environment, nodes; from featurelifted.lexer import Lexer; from featurelifted.parser import Parser`
- Callable: `featurelifted.Environment.parse`
- Signature: `parse(source: str, name: str | None = None, filename: str | None = None) -> nodes.Template`

## Excluded Behavior

- template compilation and rendering
- loaders and template inheritance
- filters, tests, extensions, async mode
- CLI, original tests, docs, packaging metadata

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `jinja2`, `jinja`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — tokenize template source into token streams
- **B002** — parse templates into AST node trees
- **B003** — support block, variable, comment, and statement delimiters
- **B004** — preserve syntax error reporting with line numbers
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: jinja2, jinja
<!-- featureliftbench:behavior-clauses:end -->
