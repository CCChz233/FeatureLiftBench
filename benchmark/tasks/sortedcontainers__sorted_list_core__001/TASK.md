# FeatureLift Task: SortedList core

Extract SortedList with add/remove/bisect, positional indexing, range iterators, and sublist invariants without importing sortedcontainers.

## Target API

- Import: `import featurelifted; from featurelifted import SortedList`
- Callable: `featurelifted.SortedList`
- Signature: `SortedList(iterable=None, key=None)`

## Excluded Behavior

- SortedKeyList, SortedDict, SortedSet, and key-function variants
- benchmarks, upstream tests, docs, and packaging metadata
- original sortedcontainers import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `sortedcontainers`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — maintain sorted order with add/update and duplicate values
- **B002** — bisect_left/bisect_right and count/index on duplicate-heavy lists
- **B003** — positional indexing and slice reads with small load factors
- **B004** — irange/islice inclusive bounds and reverse iteration
- **B005** — sublist merge/delete invariants validated via _check after _reset
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: sortedcontainers
<!-- featureliftbench:behavior-clauses:end -->
