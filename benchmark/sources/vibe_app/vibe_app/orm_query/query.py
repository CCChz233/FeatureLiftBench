"""Fluent query builder that materializes SQL AST nodes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from vibe_app.orm_query.ast import ColumnRef, JoinClause, Predicate, SelectNode
from vibe_app.state import GLOBAL_STATE


@dataclass
class Query:
    """Build a SELECT query and compile it to an AST."""

    _columns: list[str] = field(default_factory=list)
    _table: str | None = None
    _where: list[tuple[str, str, Any]] = field(default_factory=list)
    _joins: list[tuple[str, str, str, str]] = field(default_factory=list)

    def select(self, *columns: str) -> Query:
        self._columns = list(columns)
        return self

    def from_table(self, table: str) -> Query:
        self._table = table
        return self

    def where(self, column: str, op: str, value: Any) -> Query:
        self._where.append((column, op, value))
        return self

    def join(
        self,
        table: str,
        on_left: str,
        on_right: str,
        *,
        join_type: str = "inner",
    ) -> Query:
        self._joins.append((table, on_left, on_right, join_type))
        return self

    def build_ast(self) -> SelectNode:
        if not self._columns:
            raise ValueError("query must select at least one column")
        if not self._table:
            raise ValueError("query must specify a from table")

        columns = tuple(ColumnRef(name) for name in self._columns)
        predicates = tuple(
            Predicate(column=column, op=op, value=value)
            for column, op, value in self._where
        )
        joins = tuple(
            JoinClause(
                table=table,
                on_left=on_left,
                on_right=on_right,
                join_type=join_type,
            )
            for table, on_left, on_right, join_type in self._joins
        )
        ast = SelectNode(
            columns=columns,
            from_table=self._table,
            where=predicates,
            joins=joins,
        )
        queries = GLOBAL_STATE.setdefault("compiled_queries", [])
        queries.append(ast.to_dict())
        return ast
