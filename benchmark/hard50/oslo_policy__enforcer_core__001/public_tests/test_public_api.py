from __future__ import annotations

from featurelifted import ConfigOpts, Enforcer, PolicyNotAuthorized, RuleDefault


def _enforcer() -> Enforcer:
    conf = ConfigOpts()
    conf(args=[])
    enforcer = Enforcer(conf, use_conf=True)
    enforcer.register_default(RuleDefault("admin_api", "role:admin"))
    enforcer.register_default(RuleDefault("public_api", "@"))
    return enforcer


def test_admin_role_is_authorized() -> None:
    enforcer = _enforcer()
    assert enforcer.enforce("admin_api", {}, {"roles": ["admin"]}) is True


def test_missing_role_is_denied() -> None:
    enforcer = _enforcer()
    assert enforcer.enforce("admin_api", {}, {"roles": ["member"]}) is False


def test_anyone_rule_allows_empty_credentials() -> None:
    enforcer = _enforcer()
    assert enforcer.enforce("public_api", {}, {}) is True


def test_denied_rule_can_raise() -> None:
    enforcer = _enforcer()
    try:
        enforcer.enforce("admin_api", {}, {"roles": []}, do_raise=True)
    except PolicyNotAuthorized:
        return
    raise AssertionError("expected PolicyNotAuthorized")
