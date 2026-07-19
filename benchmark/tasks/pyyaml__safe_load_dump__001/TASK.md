# FeatureLift Task: Safe YAML load and dump

Extract PyYAML's safe YAML parsing and dumping behavior without exposing unsafe object construction.

## Target API

- Import: `from featurelifted import safe_load, safe_load_all, safe_dump, safe_dump_all, YAMLError; from featurelifted.constructor import ConstructorError`
- Callable: `featurelifted.safe_load`
- Signature: `safe_load(stream)`

## Excluded Behavior

- unsafe load/object construction APIs
- LibYAML C extension acceleration
- command line utilities and test fixtures

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `yaml`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — parse mappings, sequences, scalars, booleans, nulls, integers, floats, and nested documents
- **B002** — support anchors, aliases, and merge keys with SafeLoader semantics
- **B003** — dump plain Python data through SafeDumper with deterministic sort_keys behavior
- **B004** — load and dump multi-document streams
- **B005** — reject unsafe Python object tags under safe_load
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: yaml
<!-- featureliftbench:behavior-clauses:end -->
