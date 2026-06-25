from featurelifted import Rule
from featurelifted import RulesEngine
from featurelifted import evaluate_rules
from featurelifted.state import GLOBAL_STATE
from featurelifted.state import reset_state


def test_contains_operator_matches_list_membership() -> None:
    rules = [
        Rule(
            name="tag-match",
            conditions=[{"field": "tags", "op": "contains", "value": "sale"}],
            actions=[{"type": "set", "field": "eligible", "value": True}],
            priority=1,
        )
    ]

    result = evaluate_rules({"tags": ["new", "sale"]}, rules)

    assert result["eligible"] is True


def test_inc_action_accumulates_counter() -> None:
    rules = [
        Rule(
            name="bump",
            conditions=[{"field": "active", "op": "eq", "value": True}],
            actions=[{"type": "inc", "field": "visits", "value": 2}],
            priority=1,
        )
    ]

    result = evaluate_rules({"active": True, "visits": 3}, rules)

    assert result["visits"] == 5


def test_rules_engine_updates_global_state_counter() -> None:
    reset_state()
    engine = RulesEngine(
        [
            Rule(
                name="noop",
                conditions=[],
                actions=[{"type": "set", "field": "seen", "value": True}],
                priority=0,
            )
        ]
    )

    engine.evaluate({"seen": False})
    engine.evaluate({"seen": False})

    assert GLOBAL_STATE["rules_evaluated"] == 2
