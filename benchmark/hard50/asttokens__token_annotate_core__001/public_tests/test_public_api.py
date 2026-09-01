from __future__ import annotations

from featurelifted import ASTTokens


SOURCE = "x = 1 + 2\n"


def test_get_text_of_binop() -> None:
    atok = ASTTokens(SOURCE, parse=True)
    assign = atok.tree.body[0]
    assert atok.get_text(assign.value) == "1 + 2"


def test_get_text_of_assignment() -> None:
    atok = ASTTokens(SOURCE, parse=True)
    assign = atok.tree.body[0]
    assert atok.get_text(assign) == "x = 1 + 2"


def test_get_token_at_name() -> None:
    atok = ASTTokens(SOURCE, parse=True)
    token = atok.get_token(1, 0)
    assert token.string == "x"
