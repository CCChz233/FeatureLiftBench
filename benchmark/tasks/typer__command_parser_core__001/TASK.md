# FeatureLift Task: Typer command parser and CLI runner

Extract Typer CLI command building, type-hint parameter parsing, and CliRunner invocation.

## Target API

- Import: `import featurelifted as typer; from featurelifted.testing import CliRunner`
- Callable: `featurelifted.Typer`
- Signature: `Typer(name=None, **kwargs)`

## Excluded Behavior

- shell completion integration
- rich markup rendering beyond basic echo
- documentation and release tooling

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `typer`, `click`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — build commands from type-annotated functions
- **B002** — parse options, arguments, defaults, and choices
- **B003** — invoke Typer apps through CliRunner
- **B004** — nested subcommands and context passing
- **B005** — usage errors for invalid parameters
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: typer, click
<!-- featureliftbench:behavior-clauses:end -->
