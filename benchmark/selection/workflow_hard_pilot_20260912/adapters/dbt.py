"""Plain-record boundary for a lifted dbt graph selection engine."""
from fnmatch import fnmatch
from types import SimpleNamespace
import networkx as nx
from . import _engine as e


class _Method:
    def __init__(self, records, method):
        self.records, self.method = records, method

    def search(self, included, value):
        for key, node in self.records.items():
            if key not in included:
                continue
            if self.method == e.MethodName.Tag:
                match = any(fnmatch(tag, value) for tag in node.tags)
            elif self.method == e.MethodName.Package:
                match = fnmatch(node.package_name, value)
            elif self.method == e.MethodName.FQN:
                match = node.resource_type != "source" and (e.is_selected_node(node.fqn, value, False) or e.is_selected_node(node.fqn[1:], value, False))
            else:
                raise ValueError("Supported selector methods: fqn, tag, package")
            if match:
                yield key


class _Selector(e.NodeSelector):
    def __init__(self, records, graph):
        self.records = records
        self.graph = e.Graph(graph.subgraph([key for key, node in records.items() if node.config.enabled]))
        self.manifest = SimpleNamespace(nodes={key: n for key, n in records.items() if n.resource_type != "source"}, sources={key: n for key, n in records.items() if n.resource_type == "source"}, unit_tests={})

    def get_method(self, method, arguments):
        return _Method(self.records, method)


def select_nodes(nodes, include, *, exclude=(), indirect_selection="eager", resource_types=None):
    records = {}
    graph = nx.DiGraph()
    for item in nodes:
        key = item["id"]
        if key in records:
            raise ValueError("duplicate node id")
        fqn = item.get("fqn", key.split("."))
        if len(fqn) < 2:
            raise ValueError("fqn must contain package and name")
        records[key] = SimpleNamespace(unique_id=key, fqn=list(fqn), package_name=fqn[0], tags=list(item.get("tags", [])), resource_type=item.get("resource_type", "model"), depends_on_nodes=list(item.get("parents", [])), config=SimpleNamespace(enabled=item.get("enabled", True)), empty=item.get("empty", False))
        graph.add_node(key)
    for key, node in records.items():
        for parent in node.depends_on_nodes:
            if parent not in records:
                raise ValueError("unknown parent id")
            graph.add_edge(parent, key)
    if not nx.is_directed_acyclic_graph(graph):
        raise ValueError("node graph must be acyclic")
    mode = e.IndirectSelection(indirect_selection)
    token = e._mode.set(mode.value)
    try:
        included = e.parse_union(list(include), False)
        excluded = e.parse_union(list(exclude), False)
        spec = e.SelectionDifference([included, excluded], indirect_selection=mode)
        selector = _Selector(records, graph)
        selected, pending = selector.select_nodes(spec)
        # dbt applies task resource-type and empty-node filtering after selection.
        selected = {key for key in selected if not records[key].empty and (resource_types is None or records[key].resource_type in resource_types)}
        return {"selected": sorted(selected), "indirect_only": sorted(pending)}
    finally:
        e._mode.reset(token)


__all__ = ["select_nodes"]
