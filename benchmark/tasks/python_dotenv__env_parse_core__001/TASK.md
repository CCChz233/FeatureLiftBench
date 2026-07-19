# FeatureLift Task: Dotenv parse and set_key core

Extract .env file parsing with quote/escape handling, POSIX variable expansion, and set_key file mutation without importing dotenv.

## Target API

- Import: `import featurelifted; from featurelifted import dotenv_values, set_key, get_key`
- Callable: `featurelifted.dotenv_values`
- Signature: `dotenv_values(stream=..., interpolate=True, encoding='utf-8')`

## Excluded Behavior

- CLI and IPython extension entrypoints
- load_dotenv os.environ side effects in hidden tests
- upstream test suite and docs
- original dotenv import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `dotenv`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — parse key=value pairs from stream with export prefix and comments
- **B002** — single- and double-quoted values with escape sequences
- **B003** — UTF-8 BOM stripping at file start
- **B004** — POSIX ${VAR} and ${VAR:-default} variable interpolation
- **B005** — set_key creates or updates keys with auto-quoting
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: dotenv
<!-- featureliftbench:behavior-clauses:end -->
