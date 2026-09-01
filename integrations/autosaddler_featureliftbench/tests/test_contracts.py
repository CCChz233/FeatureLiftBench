from __future__ import annotations

import json
from pathlib import Path

import pytest
from autosaddler.v2.prompting.models import SessionRequest, SessionSpec

from autosaddler_featureliftbench.deepseek_provider import (
    DeepSeekProviderConfig,
    _extract_json_object,
    _parse_provider_response,
    _request_payload,
)
from autosaddler_featureliftbench.harness import (
    COMPONENT_ORDER,
    INACTIVE_COMPONENT,
    PromptCandidateValidator,
    render_prompt_appendix,
)
from autosaddler_featureliftbench.trace import bounded_trace_excerpt


def test_prompt_renderer_preserves_fixed_component_order() -> None:
    rendered = render_prompt_appendix(
        {
            "repository_inspection": "Inspect first.",
            "implementation_strategy": "Implement second.",
            "self_verification": "Verify third.",
            "completion_and_recovery": "Finish fourth.",
        }
    )
    positions = [rendered.index(text) for text in ("Inspect first", "Implement second", "Verify third", "Finish fourth")]
    assert positions == sorted(positions)


def test_inactive_baseline_renders_no_appendix() -> None:
    assert render_prompt_appendix({key: INACTIVE_COMPONENT for key in COMPONENT_ORDER}) == ""


def test_validator_rejects_private_and_training_specific_text() -> None:
    validator = PromptCandidateValidator(
        component_keys=COMPONENT_ORDER,
        max_component_chars=100,
        max_total_chars=200,
        forbidden_identifiers=("sqlparse", "train-task-001"),
    )
    baseline = {key: "" for key in COMPONENT_ORDER}
    validator(baseline)
    with pytest.raises(ValueError, match="private-evaluation"):
        validator({**baseline, "self_verification": "Read hidden_tests for answers."})
    with pytest.raises(ValueError, match="training-specific"):
        validator({**baseline, "repository_inspection": "Special-case sqlparse behavior."})


def test_trace_excerpt_redacts_secrets_private_paths_and_absolute_paths(tmp_path: Path) -> None:
    source = tmp_path / "events.jsonl"
    source.write_text(
        json.dumps(
            {
                "api_key": "do-not-copy",
                "content": "open /Users/person/project/hidden_tests/test_x.py",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    excerpt = bounded_trace_excerpt(source, max_events=5, max_chars=5000)
    encoded = json.dumps(excerpt)
    assert "do-not-copy" not in encoded
    assert "/Users/person" not in encoded
    assert "hidden_tests" not in encoded


def test_deepseek_provider_inlines_only_audited_session_assets(tmp_path: Path) -> None:
    spec = SessionSpec(
        kind="diagnose_patch",
        system_context="Use sanitized training evidence only.",
        task_prompt="Propose a generic patch.",
        skills={"policy": "Do not memorize task identifiers."},
        output_schema={
            "type": "object",
            "required": ["updates"],
            "properties": {"updates": {"type": "object"}},
        },
        workspace_files={".autosaddler/training_evidence.json": '{"failure_stage":"functional"}\n'},
        capabilities=frozenset({"read_workspace"}),
    )
    request = SessionRequest(
        session_id="session-1",
        operation_id="operation-1",
        spec=spec,
        workspace=tmp_path,
        timeout_seconds=10,
    )
    config = DeepSeekProviderConfig(
        model="deepseek/deepseek-v4-flash",
        api_key_env="FEATURELIFTBENCH_API_KEY",
        api_base_env="FEATURELIFTBENCH_API_BASE",
        max_tokens=1200,
        temperature=0,
    )
    payload = _request_payload(request, config=config, api_base="https://api.deepseek.com/v1")
    assert payload["model"] == "deepseek-v4-flash"
    assert payload["response_format"] == {"type": "json_object"}
    assert "training_evidence.json" in payload["messages"][1]["content"]
    assert "failure_stage" in payload["messages"][1]["content"]
    assert str(tmp_path) not in json.dumps(payload)


def test_deepseek_provider_parses_json_with_trailing_extra_data() -> None:
    parsed = _extract_json_object(
        '{"schema_version":"autosaddler-featureliftbench-diagnosis/v1","diagnosis":"x",'
        '"expected_effect":"y","updates":{"self_verification":"Check public behaviors."}}\n'
        '{"note":"trailing extra object"}\n'
    )
    assert parsed["diagnosis"] == "x"
    assert parsed["updates"]["self_verification"] == "Check public behaviors."


def test_deepseek_provider_parses_json_fences_and_usage() -> None:
    parsed = _extract_json_object('```json\n{"updates":{"self_verification":"Check all public behaviors."}}\n```')
    assert parsed["updates"] == {"self_verification": "Check all public behaviors."}
    content, usage = _parse_provider_response(
        {
            "id": "response-1",
            "model": "deepseek-v4-flash",
            "choices": [{"message": {"content": '{"parent_ids":["candidate-1"]}'}}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120},
        },
        model="deepseek/deepseek-v4-flash",
        duration_seconds=1.5,
        configured_settings={"max_tokens": 1200},
    )
    assert content == '{"parent_ids":["candidate-1"]}'
    assert usage.total_tokens == 120
    assert usage.provider_reported_total_tokens == 120
    assert usage.provider_correlation_id == "response-1"


def test_deepseek_provider_reads_reasoning_content_when_message_content_empty() -> None:
    content, usage = _parse_provider_response(
        {
            "id": "response-2",
            "model": "deepseek-v4-flash",
            "choices": [
                {
                    "message": {
                        "content": "",
                        "reasoning_content": '{"schema_version":"autosaddler-featureliftbench-diagnosis/v1","diagnosis":"x","expected_effect":"y","updates":{"self_verification":"Check public behaviors."}}',
                    }
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        },
        model="deepseek/deepseek-v4-flash",
        duration_seconds=0.2,
        configured_settings={"max_tokens": 8192},
    )
    parsed = _extract_json_object(content)
    assert parsed["updates"]["self_verification"] == "Check public behaviors."
    assert usage.total_tokens == 30


def test_deepseek_provider_reads_content_parts_list() -> None:
    content, _usage = _parse_provider_response(
        {
            "choices": [
                {
                    "message": {
                        "content": [{"type": "text", "text": '{"parent_ids":["candidate-1"]}'}],
                    }
                }
            ],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        },
        model="deepseek/deepseek-v4-flash",
        duration_seconds=0.1,
        configured_settings={},
    )
    assert _extract_json_object(content)["parent_ids"] == ["candidate-1"]


def test_trace_excerpt_drops_bulky_fields_and_bounds_size(tmp_path: Path) -> None:
    source = tmp_path / "events.jsonl"
    source.write_text(
        json.dumps(
            {
                "kind": "ActionEvent",
                "summary": "file_editor",
                "reasoning_content": "x" * 5000,
                "new_content": "y" * 5000,
                "old_content": "z" * 5000,
                "thought": [{"text": "Keep this thought."}],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    excerpt = bounded_trace_excerpt(source, max_events=5, max_chars=4000)
    encoded = json.dumps(excerpt)
    assert "Keep this thought." in encoded
    assert "file_editor" in encoded
    assert "reasoning_content" not in encoded
    assert "new_content" not in encoded
    assert len(encoded) < 2000
