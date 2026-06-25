# Task Design: networkx__dag_topo_core__001

Status: oracle-verified

## Why This Task

Extract NetworkX DAG topological ordering from a curated site-packages snapshot where graph class views and indegree bookkeeping are tightly coupled across modules.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| DAG algorithms | `algorithms/dag.py` | `test_topological_sort_linear_dag` (public) |
| DiGraph model | `classes/digraph.py` | `test_topological_generations_layers` |
| Exceptions | `exception.py` | `test_cycle_raises_networkx_unfeasible` |
