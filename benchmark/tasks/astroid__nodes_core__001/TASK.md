# FeatureLift Task: Astroid parse and nodes subset

Extract astroid string parsing into NodeNG trees via TreeRebuilder without inference, brain plugins, or import introspection.

## Target API

- Import: `from featurelifted import parse, nodes; from featurelifted.nodes import Module, ClassDef, FunctionDef, AsyncFunctionDef, Match`
- Callable: `featurelifted.parse`
- Signature: `parse(code: str, module_name: str = '', path: str | None = None) -> Module`

## Excluded Behavior

- inference engine and brain module overrides
- live object introspection and import graph analysis
- pylint integration and original astroid import

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `astroid`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — parse Python source into astroid Module trees
- **B002** — rebuild functions, classes, async, and match statements
- **B003** — preserve docstrings, annotations, and default arguments
- **B004** — NodeNG as_string and basic structural attributes
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: astroid
<!-- featureliftbench:behavior-clauses:end -->
