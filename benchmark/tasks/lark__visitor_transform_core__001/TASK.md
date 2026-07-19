# FeatureLift Task: Parse tree visitor and transformer

Extract Lark parse-tree Visitor, Transformer, v_args, and Discard semantics with supporting parse core as a standalone package.

## Target API

- Import: `from featurelifted import Lark, Tree, Transformer, Visitor, v_args, Discard`
- Callable: `featurelifted.Transformer`
- Signature: `Transformer.transform(tree: Tree) -> Any`

## Excluded Behavior

- standalone compiler tools and CLI
- tree reconstruction and template utilities
- original project tests and documentation

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `lark`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — walk trees with Visitor callbacks
- **B002** — transform trees bottom-up with Transformer
- **B003** — decorate transformer methods with v_args inline and tree modes
- **B004** — discard nodes using Discard sentinel
- **B005** — parse grammars needed to produce trees for transformation
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: lark
<!-- featureliftbench:behavior-clauses:end -->
