# FeatureLift Task: DAG topological sorting

Extract NetworkX directed-acyclic-graph topological sort APIs as a standalone package.

## Target API

- Import: `from featurelifted import DiGraph, Graph, topological_sort, topological_generations, lexicographical_topological_sort, is_directed_acyclic_graph; from featurelifted.exception import NetworkXError, NetworkXUnfeasible`
- Callable: `featurelifted.topological_sort`
- Signature: `topological_sort(G: DiGraph)`

## Excluded Behavior

- full NetworkX algorithm suite and drawing backends
- SciPy/NumPy graph backends
- original project tests and documentation
- graph I/O formats and generators beyond empty_graph helper

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `networkx`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — construct directed graphs and add edges
- **B002** — yield nodes in topological sort order for DAGs
- **B003** — yield lexicographically stable topological orderings
- **B004** — yield topological generations (Kahn layers)
- **B005** — detect directed acyclic graphs
- **B006** — raise NetworkXError for undirected graphs and NetworkXUnfeasible for cycles
- **B007** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B008** — the submitted package does not import forbidden upstream packages: networkx
<!-- featureliftbench:behavior-clauses:end -->
