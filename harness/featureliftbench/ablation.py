"""Agent experiment arms: Main / Public-feedback / Short-prompt.

See docs/EXPERIMENT_ARMS.md. Semantic contract (API/behaviors/hidden) is unchanged;
only workspace feedback and prompt verbosity differ.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


MOUNT_PUBLIC_TESTS_ENV = "FEATURELIFTBENCH_MOUNT_PUBLIC_TESTS"
PROMPT_STYLE_ENV = "FEATURELIFTBENCH_PROMPT_STYLE"
ABLATION_ARM_ENV = "FEATURELIFTBENCH_ABLATION_ARM"

PROMPT_STYLES = frozenset({"standard", "short"})


@dataclass(frozen=True)
class AblationOptions:
    """Resolved ablation settings for one agent run."""

    mount_public_tests: bool = False
    prompt_style: str = "standard"

    def __post_init__(self) -> None:
        style = str(self.prompt_style or "standard").strip().lower()
        if style not in PROMPT_STYLES:
            raise ValueError(f"prompt_style must be one of {sorted(PROMPT_STYLES)}, got {self.prompt_style!r}")
        object.__setattr__(self, "prompt_style", style)

    @property
    def ablation_arm(self) -> str:
        if self.mount_public_tests and self.prompt_style == "short":
            return "public_feedback_short"
        if self.mount_public_tests:
            return "public_feedback"
        if self.prompt_style == "short":
            return "short_prompt"
        return "main"

    def to_env(self) -> dict[str, str]:
        return {
            MOUNT_PUBLIC_TESTS_ENV: "1" if self.mount_public_tests else "0",
            PROMPT_STYLE_ENV: self.prompt_style,
            ABLATION_ARM_ENV: self.ablation_arm,
        }

    def summary(self) -> dict[str, Any]:
        return {
            "ablation_arm": self.ablation_arm,
            "mount_public_tests": self.mount_public_tests,
            "prompt_style": self.prompt_style,
        }


def ablation_options_from_env(env: Mapping[str, str] | None = None) -> AblationOptions:
    """Parse options from an environment mapping (empty → test-blind Main)."""

    values = env or {}
    mount_raw = str(values.get(MOUNT_PUBLIC_TESTS_ENV, "0")).strip().lower()
    mount = mount_raw not in {"0", "false", "no", "off"}
    style = str(values.get(PROMPT_STYLE_ENV, "standard")).strip().lower() or "standard"
    return AblationOptions(mount_public_tests=mount, prompt_style=style)


def resolve_ablation_options(
    *,
    profile: Mapping[str, Any] | None = None,
    env_values: Mapping[str, str] | None = None,
    process_env: Mapping[str, str] | None = None,
    mount_public_tests: bool | None = None,
    prompt_style: str | None = None,
) -> AblationOptions:
    """Resolve ablation with precedence: explicit CLI > process env > .env > profile > defaults."""

    profile = profile or {}
    env_values = env_values or {}
    process_env = process_env or {}

    if mount_public_tests is None:
        mount = _first_bool(
            process_env.get(MOUNT_PUBLIC_TESTS_ENV),
            env_values.get(MOUNT_PUBLIC_TESTS_ENV),
            profile.get("mount_public_tests"),
            default=False,
        )
    else:
        mount = bool(mount_public_tests)

    if prompt_style is None:
        style = _first_string(
            process_env.get(PROMPT_STYLE_ENV),
            env_values.get(PROMPT_STYLE_ENV),
            profile.get("prompt_style"),
            default="standard",
        )
    else:
        style = str(prompt_style).strip().lower()

    return AblationOptions(mount_public_tests=mount, prompt_style=style)


def _first_string(*values: Any, default: str) -> str:
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return default


def _first_bool(*values: Any, default: bool) -> bool:
    for value in values:
        if value is None:
            continue
        if isinstance(value, bool):
            return value
        text = str(value).strip().lower()
        if not text:
            continue
        if text in {"1", "true", "yes", "on"}:
            return True
        if text in {"0", "false", "no", "off"}:
            return False
        raise ValueError(f"invalid boolean ablation value: {value!r}")
    return default
