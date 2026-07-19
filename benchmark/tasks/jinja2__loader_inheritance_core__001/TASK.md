# FeatureLift Task: Jinja2 loader and inheritance core

Extract Jinja2 template loading and extends/block inheritance rendering.

## Target API

- Import: `from featurelifted import Environment, DictLoader; from featurelifted.exceptions import TemplateNotFound; from featurelifted.loaders import BaseLoader`
- Callable: `featurelifted.Environment.get_template`
- Signature: `get_template(name: str) -> Template`

## Excluded Behavior

- PackageLoader zip/import paths beyond DictLoader
- async rendering, extensions, bytecode cache
- CLI, original tests, docs, packaging metadata

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `jinja2`, `jinja`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — load templates via DictLoader and BaseLoader subclasses
- **B002** — resolve extends chains and block overrides
- **B003** — render nested block inheritance across multiple templates
- **B004** — support trim_blocks for layout templates
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: jinja2, jinja
<!-- featureliftbench:behavior-clauses:end -->
