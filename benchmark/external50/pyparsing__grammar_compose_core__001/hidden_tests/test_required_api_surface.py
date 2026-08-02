import featurelifted


def test_required_api_surface() -> None:
    assert hasattr(featurelifted, "Group")
    assert hasattr(featurelifted, "Keyword")
    assert hasattr(featurelifted, "Literal")
    assert hasattr(featurelifted, "OneOrMore")
    assert hasattr(featurelifted, "Optional")
    assert hasattr(featurelifted, "ParseException")
    assert hasattr(featurelifted, "ParseResults")
    assert hasattr(featurelifted, "Regex")
    assert hasattr(featurelifted, "Suppress")
    assert hasattr(featurelifted, "Word")
    assert hasattr(featurelifted, "ZeroOrMore")
    assert hasattr(featurelifted, "alphas")
    assert hasattr(featurelifted, "nums")
    assert callable(featurelifted.Word.parse_string)
    assert callable(featurelifted.Literal.parse_string)
    assert callable(featurelifted.OneOrMore.parse_string)
    assert callable(featurelifted.Group.parse_string)
    assert callable(featurelifted.ParseResults.as_list)
    assert callable(featurelifted.ParseResults.as_dict)
