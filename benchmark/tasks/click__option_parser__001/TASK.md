# FeatureLift Task: Command line option parsing and invocation

Extract Click's core command, option, argument, type conversion, and testing runner behavior.

## Target API

- Import: `import featurelifted as click; from featurelifted.testing import CliRunner`
- Callable: `featurelifted.command`
- Signature: `command(*args, **kwargs)`

## Excluded Behavior

- shell completion integration
- terminal color/style platform integrations beyond basic echo
- documentation and release tooling

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `click`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — decorate functions as commands and groups
- **B002** — parse options, flags, choices, defaults, integer ranges, and positional arguments
- **B003** — invoke commands through CliRunner and capture output, exit code, and exceptions
- **B004** — support nested groups and context object passing
- **B005** — render useful usage/error output for invalid options and bad values
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: click
<!-- featureliftbench:behavior-clauses:end -->
