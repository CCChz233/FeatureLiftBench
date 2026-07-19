# FeatureLift Task: Jinja2 extension loading

Extract Jinja2 extension registration, loading, and template integration as a standalone package.

## Target API

- Import: `from featurelifted import Environment, Extension, nodes`
- Callable: `featurelifted.Environment`
- Signature: `Environment(extensions: Sequence[str | Type[Extension]] = ()) -> Environment`

## Excluded Behavior

- i18n/gettext extension and babel integration
- async rendering and bytecode cache
- loaders and extends/include inheritance graph
- CLI, original tests, docs, packaging metadata

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `jinja2`, `jinja`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — load extensions by import path string or Extension subclass
- **B002** — register extension tags and preprocessors with Environment
- **B003** — iterate extensions in priority order
- **B004** — render templates using bundled loopcontrols and do extensions
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: jinja2, jinja
<!-- featureliftbench:behavior-clauses:end -->
