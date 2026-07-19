# FeatureLift Task: DeepDiff path and exclude subset

Extract DeepDiff structural comparison with exclude_paths and parse_path.

## Target API

- Import: `import featurelifted; from featurelifted import DeepDiff, parse_path, extract`
- Callable: `featurelifted.DeepDiff`
- Signature: `DeepDiff(t1, t2, exclude_paths=None, include_paths=None, **kwargs)`

## Excluded Behavior

- DeepSearch
- Delta patch
- original deepdiff import

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `deepdiff`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — DeepDiff dict/list value changes
- **B002** — exclude_paths and include_paths filtering
- **B003** — parse_path and extract by path expression
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: deepdiff
<!-- featureliftbench:behavior-clauses:end -->
