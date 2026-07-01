"""Shared agent API configuration loading."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .agent_adapters import AgentRunConfig
from .paths import DEFAULT_AGENT_CONFIG


DEFAULT_API_KEY_ENV = "FEATURELIFTBENCH_API_KEY"
DEFAULT_API_BASE_ENV = "FEATURELIFTBENCH_API_BASE"
DEFAULT_OPENHANDS_COMMAND_ENV = "FEATURELIFTBENCH_OPENHANDS_COMMAND"
DEFAULT_OPENHANDS_COMMAND = (
    "openhands --headless --override-with-envs --exit-without-confirmation "
    "-f {prompt_file} --json"
)


@dataclass(frozen=True)
class LoadedAgentConfig:
    """Resolved agent configuration with secrets excluded from summaries."""

    run_config: AgentRunConfig
    summary: dict[str, Any]


def load_agent_run_config(
    *,
    base_config: AgentRunConfig,
    config_path: str | Path | None = None,
    profile_name: str | None = None,
    env_file: str | Path | None = None,
) -> LoadedAgentConfig:
    """Load shared agent config and merge it into a run config.

    Precedence is:
    CLI options > profile in config file > environment file > process env.
    """

    data = _read_toml(config_path)
    selected_profile = profile_name or _string_value(data.get("profile")) or "default"
    profiles = data.get("profiles")
    profile = profiles.get(selected_profile, {}) if isinstance(profiles, dict) else {}
    if not isinstance(profile, dict):
        raise ValueError(f"agent profile must be a table: {selected_profile}")

    config_env_file = env_file or _string_value(data.get("env_file")) or ".env"
    env_values = _read_env_file(config_env_file)

    api_key_env = _string_value(profile.get("api_key_env")) or DEFAULT_API_KEY_ENV
    api_base_env = _string_value(profile.get("api_base_env")) or DEFAULT_API_BASE_ENV
    api_key = _first_non_empty(os.environ.get(api_key_env), env_values.get(api_key_env))
    api_base = _first_non_empty(
        os.environ.get(api_base_env),
        env_values.get(api_base_env),
        _string_value(profile.get("api_base")),
        _string_value(profile.get("base_url")),
    )
    model = _first_non_empty(base_config.model, _string_value(profile.get("model")))
    profile_agent_bin = _string_value(profile.get("agent_bin"))
    if _ignores_profile_agent_bin(base_config.agent):
        agent_bin = base_config.agent_bin
    else:
        agent_bin = _first_non_empty(base_config.agent_bin, profile_agent_bin)

    env = dict(base_config.env or {})
    for key, value in _agent_env_values(
        env_values,
        api_key_env=api_key_env,
        api_base_env=api_base_env,
    ).items():
        env.setdefault(key, value)
    if api_key:
        env.setdefault(api_key_env, api_key)
        _set_secret_env(env, api_key)
    if api_base:
        env.setdefault(api_base_env, api_base)
        _set_api_base_env(env, api_base)
    if model:
        env.setdefault("FEATURELIFTBENCH_MODEL", model)
        env.setdefault("MSWEA_MODEL_NAME", model)
    env.setdefault("MSWEA_CONFIGURED", "true")

    cost_limit = _string_value(profile.get("cost_limit"))
    call_limit = _string_value(profile.get("call_limit"))
    if cost_limit:
        env.setdefault("MSWEA_GLOBAL_COST_LIMIT", cost_limit)
    if call_limit:
        env.setdefault("MSWEA_GLOBAL_CALL_LIMIT", call_limit)

    extra_args = _merge_extra_args(
        _featurelift_profile_extra_args(profile, agent=base_config.agent),
        base_config.extra_args,
    )
    openhands_command = _resolve_openhands_command(
        base_config,
        profile=profile,
        env_values=env_values,
    )

    run_config = AgentRunConfig(
        agent=base_config.agent,
        agent_bin=agent_bin,
        model=model,
        config=base_config.config or _string_value(profile.get("agent_config")),
        yolo=base_config.yolo,
        timeout_seconds=base_config.timeout_seconds,
        command=openhands_command,
        extra_args=extra_args,
        env=env,
        profile=selected_profile,
    )
    summary = {
        "config_path": str(Path(config_path).resolve()) if config_path else "",
        "profile": selected_profile,
        "env_file": str(Path(config_env_file).resolve()) if config_env_file else "",
        "model": model or "",
        "agent_bin": agent_bin or "",
        "api_key_env": api_key_env,
        "api_key_present": bool(api_key),
        "api_base": api_base or "",
        "cost_limit": cost_limit or "",
        "call_limit": call_limit or "",
        "openhands_command": openhands_command if _is_openhands_agent(base_config.agent) else "",
        "openhands_command_configured": bool(openhands_command)
        if _is_openhands_agent(base_config.agent)
        else False,
    }
    return LoadedAgentConfig(run_config=run_config, summary=summary)


def _read_toml(path: str | Path | None) -> dict[str, Any]:
    if path is None:
        config_path = DEFAULT_AGENT_CONFIG
        if not config_path.exists():
            return {}
        path = config_path
    config_path = Path(path)
    if not config_path.exists():
        raise ValueError(f"agent config file not found: {config_path}")
    try:
        data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"invalid agent config TOML: {config_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"agent config must be a TOML table: {config_path}")
    return data


def _read_env_file(path: str | Path | None) -> dict[str, str]:
    if path is None:
        return {}
    env_path = Path(path)
    if not env_path.exists():
        return {}

    values: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = _strip_env_value(value.strip())
        if key:
            values[key] = value
    return values


def _strip_env_value(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _set_secret_env(env: dict[str, str], api_key: str) -> None:
    env.setdefault("FEATURELIFTBENCH_API_KEY", api_key)
    env.setdefault("OPENAI_API_KEY", api_key)
    env.setdefault("LITELLM_API_KEY", api_key)
    env.setdefault("DEEPSEEK_API_KEY", api_key)


def _set_api_base_env(env: dict[str, str], api_base: str) -> None:
    env.setdefault("FEATURELIFTBENCH_API_BASE", api_base)
    env.setdefault("OPENAI_BASE_URL", api_base)
    env.setdefault("OPENAI_API_BASE", api_base)
    env.setdefault("DEEPSEEK_API_BASE", api_base)


def _agent_env_values(
    env_values: dict[str, str],
    *,
    api_key_env: str,
    api_base_env: str,
) -> dict[str, str]:
    """Return the non-secret .env values safe to pass into an agent container."""

    selected = {api_key_env, api_base_env}
    forwarded: dict[str, str] = {}
    for key, value in env_values.items():
        if key in selected:
            forwarded[key] = value
            continue
        if not key.startswith("FEATURELIFTBENCH_"):
            continue
        if _is_api_credential_env(key) or _is_api_base_env(key):
            continue
        forwarded[key] = value
    return forwarded


def _is_api_credential_env(key: str) -> bool:
    upper = key.upper()
    return any(marker in upper for marker in ("API_KEY", "TOKEN", "SECRET", "PASSWORD"))


def _is_api_base_env(key: str) -> bool:
    upper = key.upper()
    return upper.endswith("_API_BASE") or upper.endswith("_BASE_URL")


def _string_value(value: Any) -> str:
    return value if isinstance(value, str) and value else ""


def _first_non_empty(*values: str | None) -> str:
    for value in values:
        if value:
            return value
    return ""


def _is_featurelift_agent(agent: str) -> bool:
    normalized = agent.strip().lower().replace("_", "-")
    return normalized in {"featurelift-agent", "featureliftagent", "featurelift"}


def _is_openhands_agent(agent: str) -> bool:
    normalized = agent.strip().lower().replace("_", "-")
    return normalized in {"openhands", "openhands-agent", "openhandsagent"}


def _ignores_profile_agent_bin(agent: str) -> bool:
    return _is_featurelift_agent(agent) or _is_openhands_agent(agent)


def _truthy(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, (int, float)) and value != 0:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return False


def _featurelift_profile_extra_args(profile: dict[str, Any], *, agent: str) -> tuple[str, ...]:
    if not _is_featurelift_agent(agent):
        return ()
    args: list[str] = []
    if _truthy(profile.get("featurelift_enable_llm")):
        args.append("--enable-llm")
    if _truthy(profile.get("featurelift_execute_actions")):
        args.append("--execute-actions")
    phases = _string_value(profile.get("featurelift_llm_phases"))
    if phases:
        args.extend(["--llm-phases", phases])
    repair_rounds = profile.get("featurelift_max_repair_rounds")
    if repair_rounds is not None and str(repair_rounds).strip():
        args.extend(["--max-repair-rounds", str(repair_rounds).strip()])
    tool_timeout = profile.get("featurelift_tool_timeout")
    if tool_timeout is not None and str(tool_timeout).strip():
        args.extend(["--tool-timeout", str(tool_timeout).strip()])
    return tuple(args)


def _merge_extra_args(*groups: tuple[str, ...]) -> tuple[str, ...]:
    merged: list[str] = []
    for group in groups:
        merged.extend(group)
    return tuple(merged)


def _resolve_openhands_command(
    base_config: AgentRunConfig,
    *,
    profile: dict[str, Any],
    env_values: dict[str, str],
) -> str:
    if not _is_openhands_agent(base_config.agent):
        return base_config.command
    if base_config.command:
        return base_config.command
    profile_command = _string_value(profile.get("openhands_command"))
    if profile_command:
        return profile_command
    return _first_non_empty(
        os.environ.get(DEFAULT_OPENHANDS_COMMAND_ENV),
        env_values.get(DEFAULT_OPENHANDS_COMMAND_ENV),
        DEFAULT_OPENHANDS_COMMAND,
    )
