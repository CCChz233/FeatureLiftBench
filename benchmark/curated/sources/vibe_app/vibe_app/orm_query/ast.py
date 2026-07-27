"""SQL abstract syntax tree nodes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SqlNode:
    """Base node for SQL AST fragments."""

    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError


@dataclass(frozen=True)
class ColumnRef(SqlNode):
    name: str
    table: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"type": "column", "name": self.name}
        if self.table is not None:
            payload["table"] = self.table
        return payload


@dataclass(frozen=True)
class Literal(SqlNode):
    value: Any

    def to_dict(self) -> dict[str, Any]:
        return {"type": "literal", "value": self.value}


@dataclass(frozen=True)
class Predicate(SqlNode):
    column: str
    op: str
    value: Any

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "predicate",
            "column": self.column,
            "op": self.op,
            "value": self.value,
        }


@dataclass(frozen=True)
class JoinClause(SqlNode):
    table: str
    on_left: str
    on_right: str
    join_type: str = "inner"

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "join",
            "table": self.table,
            "on_left": self.on_left,
            "on_right": self.on_right,
            "join_type": self.join_type,
        }


@dataclass(frozen=True)
class SelectNode(SqlNode):
    columns: tuple[ColumnRef, ...]
    from_table: str
    where: tuple[Predicate, ...] = field(default_factory=tuple)
    joins: tuple[JoinClause, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "select",
            "columns": [column.to_dict() for column in self.columns],
            "from": self.from_table,
            "where": [predicate.to_dict() for predicate in self.where],
            "joins": [join.to_dict() for join in self.joins],
        }
