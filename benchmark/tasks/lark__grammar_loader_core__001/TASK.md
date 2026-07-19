# FeatureLift Task: Grammar file loading

Extract Lark grammar loading from files and packages, including %import relative paths and packaged grammars/common.lark.

## Target API

- Import: `import featurelifted; from featurelifted import Lark; from featurelifted.exceptions import GrammarError; from featurelifted.load_grammar import FromPackageLoader`
- Callable: `featurelifted.Lark.open`
- Signature: `Lark.open(grammar_filename: str, rel_to: str | None = None, **options) -> Lark`

## Excluded Behavior

- standalone codegen tools and CLI
- serialization caches beyond compile-time loading
- original project tests

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `lark`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — load grammars from strings and files with Lark.open(rel_to=...)
- **B002** — resolve relative %import directives across grammar files
- **B003** — load packaged grammars via open_from_package and %import common.*
- **B004** — parse inputs with lalr after grammar compilation
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: lark
<!-- featureliftbench:behavior-clauses:end -->
