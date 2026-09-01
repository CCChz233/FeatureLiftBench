from __future__ import annotations

import json
from collections.abc import Mapping, Sequence

from autosaddler.v2.core.domain import JsonValue, canonical_json, sha256_digest
from autosaddler.v2.prompting.models import SessionSpec
from autosaddler.v2.storage.local import LocalRunStore

_SKILL = """---
name: featurelift-harness-optimization
description: Improve only generic FeatureLift task-solving policy components from train evidence.
---

# FeatureLift harness optimization

Infer task-independent process improvements from training failures. Keep the patch short, operational,
and useful across unrelated repositories. Never encode case IDs, repository names, package names,
symbols, expected answers, evaluator paths, or hidden-test details. Do not request more benchmark
information. Change the smallest set of components likely to improve Functional Pass.
"""


class FeatureLiftPromptPack:
    def __init__(
        self,
        *,
        store: LocalRunStore,
        component_keys: Sequence[str],
        max_component_chars: int,
        fixture_target_component: str = "",
        fixture_improved_text: str = "",
    ) -> None:
        self.store = store
        self.component_keys = tuple(component_keys)
        self.max_component_chars = max_component_chars
        self.fixture_target_component = fixture_target_component
        self.fixture_improved_text = fixture_improved_text

    def session(self, kind: str, context: Mapping[str, JsonValue]) -> SessionSpec:
        workspace_files = {".autosaddler/session_context.json": canonical_json(context) + "\n"}
        if kind == "diagnose_patch":
            workspace_files[".autosaddler/training_evidence.json"] = self._evidence(context.get("evidence"))
            schema = self._diagnosis_schema()
            task_prompt = (
                "Read .autosaddler/training_evidence.json and propose one generic prompt-harness patch. "
                "Return structured output only: one JSON object with schema_version, diagnosis, "
                "expected_effect, and a non-empty updates object. Updates may use only the allowed "
                "component keys. Do not wrap the JSON in Markdown."
            )
            mutation_label = "prompt_steering"
        elif kind == "evolve":
            candidate_ids = _strings(context.get("candidate_ids"), "candidate_ids")
            source_options = _source_options(context.get("component_source_options"), candidate_ids)
            schema = _evolve_schema(candidate_ids, source_options)
            task_prompt = "Select or compose accepted prompt candidates using development aggregates only."
            mutation_label = None
        elif kind == "reflect":
            schema = _reflection_schema()
            task_prompt = (
                "Derive concise task-independent lessons from matched train measurements and aggregate "
                "development feedback. Cite only training case IDs present in the session context."
            )
            mutation_label = None
        else:
            raise ValueError(f"Unknown FeatureLift prompt session kind: {kind}")

        fake_response = self._fixture_response(kind, context)
        if fake_response is not None:
            workspace_files[".autosaddler/fake_response.json"] = canonical_json(fake_response) + "\n"

        return SessionSpec(
            kind=kind,
            system_context=(
                "Optimize a reusable prompt-only harness for FeatureLiftBench. Use training evidence only. "
                "Development case details and all test data are unavailable. Obey the JSON output schema."
            ),
            task_prompt=task_prompt,
            skills={"featurelift-harness-optimization": _SKILL},
            output_schema=schema,
            workspace_files=workspace_files,
            capabilities=frozenset({"read_workspace", "edit_workspace", "load_skills"}),
            mutation_label=mutation_label,
        )

    def _evidence(self, raw: JsonValue | None) -> str:
        if not isinstance(raw, Mapping):
            raise TypeError("FeatureLift diagnosis requires an evidence artifact")
        uri = raw.get("uri")
        digest = raw.get("sha256")
        if not isinstance(uri, str) or not isinstance(digest, str):
            raise TypeError("FeatureLift evidence artifact requires uri and sha256")
        path = self.store.run_dir / uri
        payload = path.read_bytes()
        if sha256_digest(payload) != digest:
            raise ValueError("FeatureLift training evidence digest drift")
        value = json.loads(payload)
        if not isinstance(value, dict) or value.get("schema_version") != "autosaddler-featureliftbench-evidence/v1":
            raise ValueError("FeatureLift training evidence schema is invalid")
        return payload.decode("utf-8")

    def _diagnosis_schema(self) -> Mapping[str, JsonValue]:
        component_properties = {
            key: {"type": "string", "minLength": 1, "maxLength": self.max_component_chars}
            for key in self.component_keys
        }
        return {
            "type": "object",
            "required": ["schema_version", "diagnosis", "expected_effect", "updates"],
            "properties": {
                "schema_version": {"const": "autosaddler-featureliftbench-diagnosis/v1"},
                "diagnosis": {"type": "string", "minLength": 1},
                "expected_effect": {"type": "string", "minLength": 1},
                "updates": {
                    "type": "object",
                    "properties": component_properties,
                    "additionalProperties": False,
                    "minProperties": 1,
                },
            },
            "additionalProperties": False,
        }

    def _fixture_response(self, kind: str, context: Mapping[str, JsonValue]) -> Mapping[str, JsonValue] | None:
        if not self.fixture_target_component or not self.fixture_improved_text:
            return None
        if kind == "diagnose_patch":
            return {
                "schema_version": "autosaddler-featureliftbench-diagnosis/v1",
                "diagnosis": "The fixture baseline lacks the deterministic smoke instruction.",
                "expected_effect": "The fixture evaluator will recognize the bounded prompt update.",
                "updates": {self.fixture_target_component: self.fixture_improved_text},
            }
        if kind == "evolve":
            candidate_ids = _strings(context.get("candidate_ids"), "candidate_ids")
            return {
                "schema_version": "autosaddler-featureliftbench-evolution/v1",
                "parent_ids": [candidate_ids[0]],
                "component_sources": {},
                "rationale": "Use the first accepted fixture candidate.",
            }
        if kind == "reflect":
            train_ids = context.get("train_case_ids")
            evidence_ids = [item for item in train_ids if isinstance(item, str)] if isinstance(train_ids, list) else []
            return {
                "schema_version": "autosaddler-featureliftbench-reflection/v1",
                "lessons": [
                    {
                        "scope": "prompt_steering",
                        "statement": "The bounded generic prompt update improved the matched fixture batch.",
                        "evidence_case_ids": evidence_ids,
                    }
                ],
            }
        return None


def _evolve_schema(
    candidate_ids: tuple[str, ...],
    source_options: Mapping[str, tuple[str, ...]],
) -> Mapping[str, JsonValue]:
    return {
        "type": "object",
        "required": ["schema_version", "parent_ids", "component_sources", "rationale"],
        "properties": {
            "schema_version": {"const": "autosaddler-featureliftbench-evolution/v1"},
            "parent_ids": {
                "type": "array",
                "items": {"type": "string", "enum": list(candidate_ids)},
                "minItems": 1,
                "uniqueItems": True,
            },
            "component_sources": {
                "type": "object",
                "properties": {
                    key: {"type": "string", "enum": list(options)} for key, options in source_options.items()
                },
                "additionalProperties": False,
            },
            "rationale": {"type": "string", "minLength": 1},
        },
        "additionalProperties": False,
    }


def _reflection_schema() -> Mapping[str, JsonValue]:
    return {
        "type": "object",
        "required": ["schema_version", "lessons"],
        "properties": {
            "schema_version": {"const": "autosaddler-featureliftbench-reflection/v1"},
            "lessons": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["scope", "statement", "evidence_case_ids"],
                    "properties": {
                        "scope": {"type": "string", "minLength": 1},
                        "statement": {"type": "string", "minLength": 1},
                        "evidence_case_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "uniqueItems": True,
                        },
                    },
                    "additionalProperties": False,
                },
            },
        },
        "additionalProperties": False,
    }


def _strings(value: JsonValue | None, name: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value or any(not isinstance(item, str) or not item for item in value):
        raise TypeError(f"FeatureLift prompt context {name} must be a non-empty string list")
    return tuple(value)


def _source_options(value: JsonValue | None, candidate_ids: tuple[str, ...]) -> Mapping[str, tuple[str, ...]]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise TypeError("component_source_options must be an object")
    allowed = set(candidate_ids)
    result: dict[str, tuple[str, ...]] = {}
    for key, raw in value.items():
        if not isinstance(key, str) or not isinstance(raw, list):
            raise TypeError("component_source_options must map strings to string lists")
        options = tuple(item for item in raw if isinstance(item, str))
        if len(options) != len(raw) or any(item not in allowed for item in options):
            raise ValueError(f"Invalid component source options for {key}")
        result[key] = options
    return result

