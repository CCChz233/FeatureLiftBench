from __future__ import annotations

from featurelifted import AnswersMap, Question, SandboxedEnvironment, load_answersfile_data


def test_question_default() -> None:
    question = Question(
        var_name="name",
        answers=AnswersMap(),
        context={},
        jinja_env=SandboxedEnvironment(),
        type="str",
        default="alice",
    )
    assert question.get_default() == "alice"


def test_load_answersfile_data(tmp_path) -> None:
    answers = tmp_path / ".copier-answers.yml"
    answers.write_text("name: bob\n", encoding="utf-8")
    loaded = load_answersfile_data(tmp_path)
    assert loaded["name"] == "bob"


def test_invalid_choice_raises() -> None:
    question = Question(
        var_name="color",
        answers=AnswersMap(),
        context={},
        jinja_env=SandboxedEnvironment(),
        type="str",
        choices=["red", "blue"],
    )
    try:
        question.parse_answer("green")
    except ValueError as exc:
        assert "Invalid choice" in str(exc)
        return
    raise AssertionError("expected ValueError")


def test_missing_answers_file_returns_empty(tmp_path) -> None:
    loaded = load_answersfile_data(tmp_path)
    assert loaded == {}
