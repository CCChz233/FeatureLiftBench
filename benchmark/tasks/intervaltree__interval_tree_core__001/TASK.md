# FeatureLift Task: IntervalTree core

Extract IntervalTree add/remove/overlap/chop operations with Interval value semantics without importing intervaltree.

## Target API

- Import: `import featurelifted; from featurelifted import Interval, IntervalTree`
- Callable: `featurelifted.IntervalTree`
- Signature: `IntervalTree(intervals=None)`

## Excluded Behavior

- upstream test harness, benchmarks, and packaging metadata
- original intervaltree import at runtime
- CLI and documentation tooling

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `intervaltree`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — add/remove/discard intervals with set semantics and distinct data fields
- **B002** — point and range overlap queries via at/overlap/overlaps
- **B003** — remove_overlap and remove_envelop bulk deletion
- **B004** — chop trims overhanging intervals and optional datafunc relabeling
- **B005** — self-balancing tree queries through Node search helpers
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: intervaltree
<!-- featureliftbench:behavior-clauses:end -->
