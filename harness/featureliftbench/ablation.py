"""Agent experiment arms: Main / Entrypoint-Hint / Public-feedback / Short-prompt / TD / Exec-Contract / Self-Contract.

See docs/EXPERIMENT_ARMS.md. Semantic contract (API/behaviors/hidden) is unchanged.
Main is No-Hint by default; source-location hints require explicit opt-in.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


MOUNT_PUBLIC_TESTS_ENV = "FEATURELIFTBENCH_MOUNT_PUBLIC_TESTS"
PROMPT_STYLE_ENV = "FEATURELIFTBENCH_PROMPT_STYLE"
EXPOSE_SOURCE_HINTS_ENV = "FEATURELIFTBENCH_EXPOSE_SOURCE_HINTS"
SOURCE_CONTEXT_ENV = "FEATURELIFTBENCH_SOURCE_CONTEXT"
TD_COGNITION_ENV = "FEATURELIFTBENCH_TD_COGNITION"
EXEC_CONTRACT_ENV = "FEATURELIFTBENCH_EXEC_CONTRACT"
SELF_CONTRACT_ENV = "FEATURELIFTBENCH_SELF_CONTRACT"
ABLATION_ARM_ENV = "FEATURELIFTBENCH_ABLATION_ARM"

PROMPT_STYLES = frozenset({"standard", "short"})
SOURCE_CONTEXTS = frozenset({"full_repository", "pruned_context"})


@dataclass(frozen=True)
class AblationOptions:
    """Resolved ablation settings for one agent run."""

    mount_public_tests: bool = False
    prompt_style: str = "standard"
    expose_source_hints: bool = False
    source_context: str = "full_repository"
    td_cognition: bool = False
    exec_contract: bool = False
    self_contract: bool = False

    def __post_init__(self) -> None:
        style = str(self.prompt_style or "standard").strip().lower()
        if style not in PROMPT_STYLES:
            raise ValueError(f"prompt_style must be one of {sorted(PROMPT_STYLES)}, got {self.prompt_style!r}")
        object.__setattr__(self, "prompt_style", style)
        source_context = str(self.source_context or "full_repository").strip().lower()
        if source_context not in SOURCE_CONTEXTS:
            raise ValueError(
                f"source_context must be one of {sorted(SOURCE_CONTEXTS)}, "
                f"got {self.source_context!r}"
            )
        object.__setattr__(self, "source_context", source_context)
        object.__setattr__(self, "td_cognition", bool(self.td_cognition))
        object.__setattr__(self, "exec_contract", bool(self.exec_contract))
        object.__setattr__(self, "self_contract", bool(self.self_contract))
        method_arms = sum(
            1 for flag in (self.td_cognition, self.exec_contract, self.self_contract) if flag
        )
        if method_arms > 1:
            raise ValueError(
                "td_cognition, exec_contract, and self_contract are mutually exclusive"
            )

    @property
    def ablation_arm(self) -> str:
        if self.self_contract:
            return "self_contract"
        if self.exec_contract:
            return "exec_contract"
        if self.td_cognition:
            return "td_cognition"
        parts: list[str] = []
        if self.expose_source_hints:
            parts.append("entrypoint_hint")
        if self.mount_public_tests:
            parts.append("public_feedback")
        if self.prompt_style == "short":
            parts.append("short_prompt")
        if self.source_context == "pruned_context":
            parts.append("pruned_context")
        return "_".join(parts) if parts else "main"

    def to_env(self) -> dict[str, str]:
        return {
            MOUNT_PUBLIC_TESTS_ENV: "1" if self.mount_public_tests else "0",
            PROMPT_STYLE_ENV: self.prompt_style,
            EXPOSE_SOURCE_HINTS_ENV: "1" if self.expose_source_hints else "0",
            SOURCE_CONTEXT_ENV: self.source_context,
            TD_COGNITION_ENV: "1" if self.td_cognition else "0",
            EXEC_CONTRACT_ENV: "1" if self.exec_contract else "0",
            SELF_CONTRACT_ENV: "1" if self.self_contract else "0",
            ABLATION_ARM_ENV: self.ablation_arm,
        }

    def summary(self) -> dict[str, Any]:
        return {
            "ablation_arm": self.ablation_arm,
            "mount_public_tests": self.mount_public_tests,
            "prompt_style": self.prompt_style,
            "expose_source_hints": self.expose_source_hints,
            "source_context": self.source_context,
            "td_cognition": self.td_cognition,
            "exec_contract": self.exec_contract,
            "self_contract": self.self_contract,
        }


def ablation_options_from_env(env: Mapping[str, str] | None = None) -> AblationOptions:
    """Parse options from an environment mapping (empty → test-blind Main)."""

    values = env or {}
    mount_raw = str(values.get(MOUNT_PUBLIC_TESTS_ENV, "0")).strip().lower()
    mount = mount_raw not in {"0", "false", "no", "off"}
    style = str(values.get(PROMPT_STYLE_ENV, "standard")).strip().lower() or "standard"
    hints_raw = str(values.get(EXPOSE_SOURCE_HINTS_ENV, "0")).strip().lower()
    expose_hints = hints_raw not in {"0", "false", "no", "off"}
    source_context = (
        str(values.get(SOURCE_CONTEXT_ENV, "full_repository")).strip().lower()
        or "full_repository"
    )
    td_raw = str(values.get(TD_COGNITION_ENV, "0")).strip().lower()
    td_cognition = td_raw not in {"0", "false", "no", "off", ""}
    ec_raw = str(values.get(EXEC_CONTRACT_ENV, "0")).strip().lower()
    exec_contract = ec_raw not in {"0", "false", "no", "off", ""}
    sc_raw = str(values.get(SELF_CONTRACT_ENV, "0")).strip().lower()
    self_contract = sc_raw not in {"0", "false", "no", "off", ""}
    return AblationOptions(
        mount_public_tests=mount,
        prompt_style=style,
        expose_source_hints=expose_hints,
        source_context=source_context,
        td_cognition=td_cognition,
        exec_contract=exec_contract,
        self_contract=self_contract,
    )


def resolve_ablation_options(
    *,
    profile: Mapping[str, Any] | None = None,
    env_values: Mapping[str, str] | None = None,
    process_env: Mapping[str, str] | None = None,
    mount_public_tests: bool | None = None,
    prompt_style: str | None = None,
    expose_source_hints: bool | None = None,
    source_context: str | None = None,
    td_cognition: bool | None = None,
    exec_contract: bool | None = None,
    self_contract: bool | None = None,
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

    if expose_source_hints is None:
        expose_hints = _first_bool(
            process_env.get(EXPOSE_SOURCE_HINTS_ENV),
            env_values.get(EXPOSE_SOURCE_HINTS_ENV),
            profile.get("expose_source_hints"),
            default=False,
        )
    else:
        expose_hints = bool(expose_source_hints)

    if source_context is None:
        resolved_source_context = _first_string(
            process_env.get(SOURCE_CONTEXT_ENV),
            env_values.get(SOURCE_CONTEXT_ENV),
            profile.get("source_context"),
            default="full_repository",
        )
    else:
        resolved_source_context = str(source_context).strip().lower()

    if td_cognition is None:
        resolved_td = _first_bool(
            process_env.get(TD_COGNITION_ENV),
            env_values.get(TD_COGNITION_ENV),
            profile.get("td_cognition"),
            default=False,
        )
    else:
        resolved_td = bool(td_cognition)

    if exec_contract is None:
        resolved_ec = _first_bool(
            process_env.get(EXEC_CONTRACT_ENV),
            env_values.get(EXEC_CONTRACT_ENV),
            profile.get("exec_contract"),
            default=False,
        )
    else:
        resolved_ec = bool(exec_contract)

    if self_contract is None:
        resolved_sc = _first_bool(
            process_env.get(SELF_CONTRACT_ENV),
            env_values.get(SELF_CONTRACT_ENV),
            profile.get("self_contract"),
            default=False,
        )
    else:
        resolved_sc = bool(self_contract)

    return AblationOptions(
        mount_public_tests=mount,
        prompt_style=style,
        expose_source_hints=expose_hints,
        source_context=resolved_source_context,
        td_cognition=resolved_td,
        exec_contract=resolved_ec,
        self_contract=resolved_sc,
    )


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
