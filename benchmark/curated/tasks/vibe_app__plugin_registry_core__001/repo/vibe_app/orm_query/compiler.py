"""Compile Query objects and SQL AST nodes to SQL strings."""

from __future__ import annotations

from typing import Any

from vibe_app.orm_query.ast import (
    ColumnRef,
    JoinClause,
    Literal,
    Predicate,
    SelectNode,
    SqlNode,
)
from vibe_app.orm_query.query import Query
from vibe_app.state import GLOBAL_STATE


_OP_SQL = {
    "eq": "=",
    "neq": "!=",
    "gt": ">",
    "gte": ">=",
    "lt": "<",
    "lte": "<=",
}


def _quote(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return str(value)
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"


def _render_column(column: ColumnRef) -> str:
    if column.table:
        return f"{column.table}.{column.name}"
    return column.name


def _render_predicate(predicate: Predicate) -> str:
    op = _OP_SQL.get(predicate.op)
    if op is None:
        raise ValueError(f"unsupported predicate operator: {predicate.op}")
    return f"{predicate.column} {op} {_quote(predicate.value)}"


def _render_join(join: JoinClause) -> str:
    join_keyword = join.join_type.upper()
    if join_keyword == "INNER":
        join_keyword = "INNER JOIN"
    else:
        join_keyword = f"{join_keyword} JOIN"
    return (
        f"{join_keyword} {join.table} "
        f"ON {join.on_left} = {join.on_right}"
    )


def compile_ast(node: SqlNode) -> str:
    """Render a SQL AST node as a SQL string."""
    if isinstance(node, SelectNode):
        columns = ", ".join(_render_column(column) for column in node.columns)
        sql = f"SELECT {columns} FROM {node.from_table}"
        for join in node.joins:
            sql += f" {_render_join(join)}"
        if node.where:
            predicates = " AND ".join(_render_predicate(predicate) for predicate in node.where)
            sql += f" WHERE {predicates}"
        return sql
    if isinstance(node, Literal):
        return _quote(node.value)
    if isinstance(node, ColumnRef):
        return _render_column(node)
    if isinstance(node, Predicate):
        return _render_predicate(node)
    if isinstance(node, JoinClause):
        return _render_join(node)
    raise TypeError(f"unsupported SQL AST node: {type(node)!r}")


def compile_query(query: Query) -> str:
    """Build and compile a Query to SQL."""
    ast = query.build_ast()
    sql = compile_ast(ast)
    GLOBAL_STATE.setdefault("last_compiled_sql", sql)
    return sql
