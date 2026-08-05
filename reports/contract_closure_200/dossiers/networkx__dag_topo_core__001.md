# networkx__dag_topo_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `7/17`

## Required API

- `featurelifted.DiGraph` (class) `(incoming_graph_data=None, **attr)`
- `featurelifted.Graph` (class) `(incoming_graph_data=None, **attr)`
- `featurelifted.topological_sort` (function) `(G, *, backend=None, **backend_kwargs)`
- `featurelifted.topological_generations` (function) `(G, *, backend=None, **backend_kwargs)`
- `featurelifted.lexicographical_topological_sort` (function) `(G, key=None, *, backend=None, **backend_kwargs)`
- `featurelifted.is_directed_acyclic_graph` (function) `(G, *, backend=None, **backend_kwargs)`
- `featurelifted.exception` (module)
- `featurelifted.exception.NetworkXError` (exception)
- `featurelifted.exception.NetworkXUnfeasible` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: construct directed graphs and add edges. Required observable cases include undirected graph raises networkx error.
- **B002**: The extracted feature must support this observable behavior: yield nodes in topological sort order for DAGs. Required observable cases include topological sort linear dag; topological sort parallel roots; lexicographical topological sort is stable.
- **B003**: The extracted feature must support this observable behavior: yield lexicographically stable topological orderings. Required observable cases include lexicographical topological sort is stable.
- **B004**: The extracted feature must support this observable behavior: yield topological generations (Kahn layers). Required observable cases include topological generations layers.
- **B005**: The extracted feature must support this observable behavior: detect directed acyclic graphs. Required observable cases include undirected graph raises networkx error.
- **B006**: The extracted feature must support this observable behavior: raise NetworkXError for undirected graphs and NetworkXUnfeasible for cycles. Required observable cases include cycle raises networkx unfeasible; undirected graph raises networkx error.
- **B007**: The package exposes the required task API paths `featurelifted.DiGraph`, `featurelifted.Graph`, `featurelifted.topological_sort`, `featurelifted.topological_generations`, `featurelifted.lexicographical_topological_sort`, `featurelifted.is_directed_acyclic_graph`, `featurelifted.exception`, `featurelifted.exception.NetworkXError`, `featurelifted.exception.NetworkXUnfeasible` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_topological_sort_linear_dag`

- mapping: `B002`
- API: `featurelifted.DiGraph, featurelifted.is_directed_acyclic_graph, featurelifted.topological_sort`
- risk: `none`
- A001 `assert` L11: `list(topological_sort(graph)) == ['a', 'b', 'c']`
- A002 `assert` L12: `is_directed_acyclic_graph(graph) is True`

### `public_tests/test_public_api.py::test_topological_sort_parallel_roots`

- mapping: `B002`
- API: `featurelifted.DiGraph, featurelifted.topological_sort`
- risk: `none`
- A001 `assert` L20: `order.index('a') < order.index('c')`
- A002 `assert` L21: `order.index('b') < order.index('c')`

### `hidden_tests/test_hidden_behavior.py::test_lexicographical_topological_sort_is_stable`

- mapping: `B002, B003`
- API: `featurelifted.DiGraph, featurelifted.exception, featurelifted.lexicographical_topological_sort`
- risk: `none`
- A001 `assert` L15: `list(lexicographical_topological_sort(graph)) == ['c', 'a', 'b', 'd']`

### `hidden_tests/test_hidden_behavior.py::test_topological_generations_layers`

- mapping: `B004`
- API: `featurelifted.DiGraph, featurelifted.exception, featurelifted.topological_generations`
- risk: `none`
- A001 `assert` L23: `generations == [['c'], ['a'], ['b'], ['d']]`

### `hidden_tests/test_hidden_behavior.py::test_cycle_raises_networkx_unfeasible`

- mapping: `B006`
- API: `featurelifted.DiGraph, featurelifted.exception, featurelifted.topological_sort`
- risk: `exception_semantics`
- A001 `raises` L29: `pytest.raises(NetworkXUnfeasible)`

### `hidden_tests/test_hidden_behavior.py::test_undirected_graph_raises_networkx_error`

- mapping: `B001, B005, B006`
- API: `featurelifted.Graph, featurelifted.exception, featurelifted.topological_sort`
- risk: `exception_semantics`
- A001 `raises` L36: `pytest.raises(NetworkXError)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B007`
- API: `featurelifted.DiGraph, featurelifted.Graph, featurelifted.exception, featurelifted.is_directed_acyclic_graph, featurelifted.lexicographical_topological_sort, featurelifted.topological_generations, featurelifted.topological_sort`
- risk: `none`
- A001 `assert` L15: `isinstance(DiGraph, type)`
- A002 `assert` L16: `isinstance(Graph, type)`
- A003 `assert` L17: `callable(topological_sort)`
- A004 `assert` L18: `callable(topological_generations)`
- A005 `assert` L19: `callable(lexicographical_topological_sort)`
- A006 `assert` L20: `callable(is_directed_acyclic_graph)`
- A007 `assert` L21: `exception is not None`
- A008 `assert` L22: `issubclass(getattr(exception, 'NetworkXError'), BaseException)`
- A009 `assert` L23: `issubclass(getattr(exception, 'NetworkXUnfeasible'), BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `networkx`
- source entrypoints: `networkx.DiGraph, networkx.topological_sort, networkx.lexicographical_topological_sort, networkx.topological_generations, networkx.is_directed_acyclic_graph, networkx.NetworkXError, networkx.NetworkXUnfeasible`
- oracle source files: `networkx/__init__.py, networkx/exception.py, networkx/lazy_imports.py, networkx/convert.py, networkx/utils/__init__.py, networkx/utils/backends.py, networkx/utils/configs.py, networkx/utils/decorators.py, networkx/utils/misc.py, networkx/utils/heaps.py, networkx/utils/mapped_queue.py, networkx/utils/random_sequence.py, networkx/utils/union_find.py, networkx/utils/rcm.py, networkx/classes/__init__.py, networkx/classes/coreviews.py, networkx/classes/reportviews.py, networkx/classes/filters.py, networkx/classes/graph.py, networkx/classes/digraph.py, networkx/classes/function.py, networkx/classes/graphviews.py, networkx/generators/__init__.py, networkx/generators/classic.py, networkx/algorithms/__init__.py, networkx/algorithms/dag.py`
- runtime dependencies: `none`
- oracle notes: Curated DAG topological-sort closure from NetworkX 3.3 site-packages snapshot.
