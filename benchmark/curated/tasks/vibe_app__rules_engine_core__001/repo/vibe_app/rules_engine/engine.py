"""Canonical rules engine orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from vibe_app.rules_engine.actions import apply_actions
from vibe_app.rules_engine.conditions import match_condition
from vibe_app.state import GLOBAL_STATE


@dataclass
class Rule:
    name: str
    conditions: list[dict[str, Any]]
    actions: list[dict[str, Any]]
    priority: int = 0


@dataclass
class RulesEngine:
    rules: list[Rule] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.rules = sorted(self.rules, key=lambda rule: (-rule.priority, rule.name))

    def evaluate(self, facts: dict[str, Any]) -> dict[str, Any]:
        result = dict(facts)
        for rule in self.rules:
            if all(match_condition(condition, result) for condition in rule.conditions):
                result = apply_actions(rule.actions, result)
        GLOBAL_STATE.setdefault("rules_evaluated", 0)
        GLOBAL_STATE["rules_evaluated"] += 1
        return result


def evaluate_rules(facts: dict[str, Any], rules: list[Rule]) -> dict[str, Any]:
    """Evaluate rules against facts using the canonical engine."""
    return RulesEngine(rules).evaluate(facts)
