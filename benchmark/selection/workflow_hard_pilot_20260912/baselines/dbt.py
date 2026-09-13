"""Plausible selector with graph expansion; indirect tests are added once at end.

This models a natural flatten-then-evaluate implementation instead of a stub.
"""
from fnmatch import fnmatch
import re
import networkx as nx


def select_nodes(nodes, include, *, exclude=(), indirect_selection="eager", resource_types=None):
    if indirect_selection not in {"eager", "cautious", "buildable", "empty"}:
        raise ValueError(indirect_selection)
    by_id = {n["id"]: n for n in nodes}
    if len(by_id) != len(nodes):
        raise ValueError("duplicate id")
    graph = nx.DiGraph()
    graph.add_nodes_from(by_id)
    for key, node in by_id.items():
        if len(node.get("fqn", key.split("."))) < 2:
            raise ValueError("short fqn")
        for parent in node.get("parents", []):
            if parent not in by_id:
                raise ValueError("unknown parent")
            graph.add_edge(parent, key)
    if not nx.is_directed_acyclic_graph(graph):
        raise ValueError("cycle")
    graph = graph.subgraph([key for key, node in by_id.items() if node.get("enabled", True)])

    def expand(seed, reverse, depth):
        result = set(seed)
        frontier = set(seed)
        step = 0
        while frontier and (depth is None or step < depth):
            neighbors = set()
            for key in frontier:
                neighbors.update(graph.predecessors(key) if reverse else graph.successors(key))
            frontier = neighbors - result
            result.update(neighbors)
            step += 1
        return result

    def term(raw):
        at = raw.startswith("@")
        if at:
            raw = raw[1:]
        match = re.fullmatch(r"(?:(\d*)\+)?(.+?)(?:\+(\d*))?", raw)
        if not match:
            raise ValueError(raw)
        before, expression, after = match.groups()
        if at and after is not None:
            raise ValueError(raw)
        method, sep, value = expression.partition(":")
        if not sep:
            method, value = "fqn", expression
        if method not in {"fqn", "tag", "package"}:
            raise ValueError(method)
        result = set()
        for key in graph:
            node = by_id[key]
            fqn = node.get("fqn", key.split("."))
            matches = any(fnmatch(t, value) for t in node.get("tags", [])) if method == "tag" else fnmatch(fqn[0], value) if method == "package" else (fnmatch(".".join(fqn), value) or fnmatch(".".join(fqn[1:]), value) or fnmatch(fqn[-1], value)) and node.get("resource_type", "model") != "source"
            if matches:
                result.add(key)
        seeds = set(result)
        if before is not None:
            result |= expand(seeds, True, int(before) if before else None)
        if after is not None:
            result |= expand(seeds, False, int(after) if after else None)
        if at:
            result = expand(expand(seeds, False, None), True, None)
        return result

    def combined(expressions):
        result = set()
        for argument in expressions:
            for union_term in argument.split():
                terms = [term(part) for part in union_term.split(",")]
                result |= set.intersection(*terms)
        return result

    selected = combined(include) - combined(exclude)
    pending = set()
    if indirect_selection != "empty":
        for key in graph:
            node = by_id[key]
            parents = set(node.get("parents", []))
            if node.get("resource_type") != "test" or not parents.intersection(selected):
                continue
            available = expand(selected, True, None) if indirect_selection == "buildable" else selected
            if indirect_selection == "eager" or parents <= available:
                selected.add(key)
            else:
                pending.add(key)
    filtered = [key for key in selected if not by_id[key].get("empty", False) and (resource_types is None or by_id[key].get("resource_type", "model") in resource_types)]
    return dict(selected=sorted(filtered), indirect_only=sorted(pending - selected))
