from featurelifted import Rule
from featurelifted import evaluate_rules


def test_rule_applies_set_action_when_condition_matches() -> None:
    rules = [
        Rule(
            name="vip-label",
            conditions=[{"field": "tier", "op": "eq", "value": "gold"}],
            actions=[{"type": "set", "field": "label", "value": "VIP"}],
            priority=1,
        )
    ]

    result = evaluate_rules({"tier": "gold", "label": "standard"}, rules)

    assert result["label"] == "VIP"


def test_multiple_rules_apply_in_priority_order() -> None:
    rules = [
        Rule(
            name="low",
            conditions=[
                {"field": "score", "op": "gte", "value": 10},
                {"field": "score", "op": "lt", "value": 50},
            ],
            actions=[{"type": "set", "field": "band", "value": "low"}],
            priority=1,
        ),
        Rule(
            name="high",
            conditions=[{"field": "score", "op": "gte", "value": 50}],
            actions=[{"type": "set", "field": "band", "value": "high"}],
            priority=10,
        ),
    ]

    assert evaluate_rules({"score": 25}, rules)["band"] == "low"
    assert evaluate_rules({"score": 75}, rules)["band"] == "high"
