"""Stable JSON boundary for upstream column lineage; no HTML rendering."""
import json
from ._sqlglot.lineage import lineage
from ._sqlglot.errors import SqlglotError


def trace_column(column, sql, *, schema=None, sources=None):
    try:
        root = lineage(column, sql, schema=schema, sources=sources, dialect="postgres")
        def encode(node):
            children = [encode(child) for child in node.downstream]
            children.sort(key=lambda child: json.dumps(child, sort_keys=True, ensure_ascii=True))
            return {"name": node.name, "expression": node.expression.sql(dialect="postgres"), "source_name": node.source_name, "reference_node_name": node.reference_node_name, "downstream": children}
        return encode(root)
    except SqlglotError as exc:
        raise ValueError(str(exc)) from exc


__all__ = ["trace_column"]
