# FeatureLift Task: Bidirectional mapping core

Extract bidict mutable/frozen/ordered bidirectional mappings with inverse views, duplicate policies, and ordered move_to_end without importing bidict.

## Target API

- Import: `import featurelifted; from featurelifted import bidict, frozenbidict, OrderedBidict, ON_DUP_RAISE, ValueDuplicationError, KeyAndValueDuplicationError, inverted`
- Callable: `featurelifted.bidict`
- Signature: `bidict(arg=(), /, **kw)`

## Excluded Behavior

- upstream benchmarks, docs, and test suite
- original bidict import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `bidict`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — forward and inverse lookups on bidict and frozenbidict
- **B002** — inverse view reflects live updates on mutable bidicts
- **B003** — ON_DUP_RAISE duplicate value/key policies with typed errors
- **B004** — OrderedBidict preserves insertion order and move_to_end
- **B005** — inverted() iterator helper for value-key pairs
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: bidict
<!-- featureliftbench:behavior-clauses:end -->
