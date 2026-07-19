# FeatureLift Task: Entry point discovery and selection

Extract importlib_metadata entry point parsing, EntryPoints selection, and PathDistribution metadata reading.

## Target API

- Import: `from featurelifted import EntryPoint, EntryPoints, PathDistribution, Sectioned`
- Callable: `featurelifted.EntryPoints.select`
- Signature: `EntryPoints.select(**params) -> EntryPoints`

## Excluded Behavior

- full distribution discovery across sys.path
- package file listing and requirements resolution
- original project tests and CLI

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `importlib_metadata`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — parse entry point definitions from metadata
- **B002** — select entry points by group and name
- **B003** — load entry point targets
- **B004** — read entry points from PathDistribution metadata directories
- **B005** — parse INI-style sectioned entry point config
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: importlib_metadata
<!-- featureliftbench:behavior-clauses:end -->
