"""Constitution API-surface coverage generated from public_spec."""

from featurelifted import (
    Rule,
    RulesEngine,
    evaluate_rules,
    state,
)


def test_required_api_surface():
    assert isinstance(Rule, type)
    assert isinstance(RulesEngine, type)
    assert hasattr(RulesEngine, 'evaluate')
    assert callable(evaluate_rules)
    assert state is not None
    assert getattr(state, 'GLOBAL_STATE') is not None
    assert callable(getattr(state, 'reset_state'))
