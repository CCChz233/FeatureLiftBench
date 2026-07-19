# FeatureLift Task: ZPT template compile and render

Extract Chameleon PageTemplate compile/render with TAL/TALES without importing chameleon.

## Target API

- Import: `from featurelifted import TemplateError; from featurelifted.zpt.template import PageTemplate`
- Callable: `featurelifted.zpt.template.PageTemplate`
- Signature: `PageTemplate(source: str, **config)`

## Excluded Behavior

- filesystem PageTemplateFile loader and auto_reload
- i18n translation catalogs beyond defaults
- benchmark utilities and legacy loader paths
- original chameleon import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `chameleon`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — compile and render PageTemplate from source strings
- **B002** — TAL attributes content/repeat/condition
- **B003** — TALES path and python expressions
- **B004** — macro define/use via metal namespace
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: chameleon
<!-- featureliftbench:behavior-clauses:end -->
