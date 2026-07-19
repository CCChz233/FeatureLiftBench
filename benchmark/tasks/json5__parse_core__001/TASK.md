# FeatureLift Task: JSON5 parse and loads

Extract json5's parser-driven loads API as a standalone package.

## Target API

- Import: `from featurelifted import loads, load`
- Callable: `featurelifted.loads`
- Signature: `loads(s: str, *, allow_duplicate_keys: bool = True) -> object`

## Excluded Behavior

- json5 dump/dumps serialization
- CLI tool and arg_parser modules
- original project tests and documentation

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `json5`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — parse JSON5 objects, arrays, strings, numbers, booleans, and null
- **B002** — support unquoted keys, single-quoted strings, trailing commas, and comments
- **B003** — support hexadecimal and leading-plus numeric literals
- **B004** — raise ValueError with line/column context for malformed input
- **B005** — optional duplicate-key rejection via allow_duplicate_keys=False
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: json5
<!-- featureliftbench:behavior-clauses:end -->
