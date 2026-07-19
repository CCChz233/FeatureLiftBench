# FeatureLift Task: Jinja2 compile and render core

Extract Jinja2 template compilation and rendering as a standalone package.

## Target API

- Import: `from featurelifted import Environment; from featurelifted.compiler import generate; from featurelifted.runtime import Context`
- Callable: `featurelifted.Environment.from_string`
- Signature: `from_string(source: str, globals: dict | None = None) -> Template`

## Excluded Behavior

- loaders and extends/include inheritance graph
- async rendering
- extensions, bytecode cache, i18n
- CLI, original tests, docs, packaging metadata

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `jinja2`, `jinja`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — compile template source to executable code
- **B002** — render templates with context variables
- **B003** — support if/for/set/macro blocks and expressions
- **B004** — preserve undefined variable behavior with default Undefined
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: jinja2, jinja
<!-- featureliftbench:behavior-clauses:end -->
