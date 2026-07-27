"""Rule action application."""

from __future__ import annotations

from typing import Any


def apply_actions(actions: list[dict[str, Any]], facts: dict[str, Any]) -> dict[str, Any]:
    """Apply a list of actions to facts and return the updated mapping."""
    result = dict(facts)
    for action in actions:
        kind = action.get("type")
        if kind == "set":
            result[action["field"]] = action["value"]
        elif kind == "inc":
            field = action["field"]
            result[field] = int(result.get(field, 0)) + int(action["value"])
        elif kind == "append":
            field = action["field"]
            items = list(result.get(field, []))
            items.append(action["value"])
            result[field] = items
    return result
