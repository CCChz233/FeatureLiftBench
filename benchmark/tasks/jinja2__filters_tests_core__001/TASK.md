# FeatureLift Task: Jinja2 filters and tests core

Extract Jinja2 built-in filters, tests, and template usage via Environment.

## Target API

- Import: `from featurelifted import Environment, filters, tests; from featurelifted.runtime import Undefined`
- Callable: `featurelifted.Environment.call_filter`
- Signature: `call_filter(name: str, value: object, *args, **kwargs) -> object`

## Excluded Behavior

- custom extension filters
- async filter variants
- loaders and template inheritance beyond from_string
- CLI, original tests, docs, packaging metadata

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `jinja2`, `jinja`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — apply built-in filters in templates and via call_filter
- **B002** — evaluate built-in tests in templates and via call_test
- **B003** — support common filters: capitalize, default, length, join, map, select
- **B004** — support common tests: defined, undefined, even, odd, number, string
- **B005** — default filter honors boolean true to treat falsey values as missing
- **B006** — runtime Undefined and filters/tests registries must be available for call_filter/call_test
- **B007** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B008** — the submitted package does not import forbidden upstream packages: jinja2, jinja
<!-- featureliftbench:behavior-clauses:end -->
