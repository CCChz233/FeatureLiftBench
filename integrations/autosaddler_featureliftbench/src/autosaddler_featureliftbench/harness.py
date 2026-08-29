from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path

COMPONENT_ORDER = (
    "repository_inspection",
    "implementation_strategy",
    "self_verification",
    "completion_and_recovery",
)

COMPONENT_HEADINGS = {
    "repository_inspection": "Repository inspection strategy",
    "implementation_strategy": "Implementation strategy",
    "self_verification": "Self-verification strategy",
    "completion_and_recovery": "Completion and recovery strategy",
}

INACTIVE_COMPONENT = "__AUTOSADDLER_FLB_INACTIVE__"

_PRIVATE_MARKERS = (
    "hidden_tests",
    "hidden test",
    "reference_solution",
    "reference solution",
    "evaluation/",
    "eval/result.json",
)


class PromptCandidateValidator:
    def __init__(
        self,
        *,
        component_keys: Sequence[str],
        max_component_chars: int,
        max_total_chars: int,
        forbidden_identifiers: Sequence[str],
    ) -> None:
        self.component_keys = tuple(component_keys)
        self.max_component_chars = max_component_chars
        self.max_total_chars = max_total_chars
        self.forbidden_identifiers = tuple(
            sorted({item.strip().lower() for item in forbidden_identifiers if len(item.strip()) >= 4})
        )

    def __call__(self, components: Mapping[str, str]) -> None:
        if tuple(sorted(components)) != tuple(sorted(self.component_keys)):
            raise ValueError("Prompt candidate component keys are frozen")
        total = 0
        joined: list[str] = []
        for key in self.component_keys:
            text = components[key]
            if len(text) > self.max_component_chars:
                raise ValueError(f"Prompt component {key!r} exceeds {self.max_component_chars} characters")
            if "\x00" in text:
                raise ValueError(f"Prompt component {key!r} contains a NUL byte")
            total += len(text)
            joined.append(text)
        if total > self.max_total_chars:
            raise ValueError(f"Prompt candidate exceeds {self.max_total_chars} total characters")
        normalized = "\n".join(joined).lower()
        private = next((marker for marker in _PRIVATE_MARKERS if marker in normalized), None)
        if private is not None:
            raise ValueError(f"Prompt candidate contains a private-evaluation marker: {private}")
        memorized = next(
            (
                identifier
                for identifier in self.forbidden_identifiers
                if re.search(rf"(?<![a-z0-9_]){re.escape(identifier)}(?![a-z0-9_])", normalized)
            ),
            None,
        )
        if memorized is not None:
            raise ValueError(f"Prompt candidate contains a training-specific identifier: {memorized}")


def load_components(materialized_root: Path) -> dict[str, str]:
    value = json.loads((materialized_root / "candidate.json").read_text(encoding="utf-8"))
    if not isinstance(value, dict) or any(not isinstance(key, str) or not isinstance(text, str) for key, text in value.items()):
        raise TypeError("Materialized prompt candidate must map strings to strings")
    return dict(value)


def render_prompt_appendix(components: Mapping[str, str]) -> str:
    sections = [
        f"### {COMPONENT_HEADINGS[key]}\n\n{components[key].strip()}"
        for key in COMPONENT_ORDER
        if components.get(key, "").strip()
        and components.get(key, "").strip() != INACTIVE_COMPONENT
    ]
    if not sections:
        return ""
    return (
        "Apply these task-independent working policies while obeying the public task contract and workspace boundaries.\n\n"
        + "\n\n".join(sections)
        + "\n"
    )
