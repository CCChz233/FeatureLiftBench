"""LLM environment normalization for external agent runtimes."""

from __future__ import annotations

from urllib.parse import urlsplit


def normalize_api_model_name(model: str, api_base: str = "") -> str:
    """Return the provider-facing model id for OpenAI-compatible APIs."""
    if not model:
        return ""
    if "api.deepseek.com" in api_base and model.startswith("deepseek/"):
        return model.split("/", 1)[1]
    if _is_local_openai_compatible_base(api_base) and model.startswith("openai/"):
        return model.split("/", 1)[1]
    return model


def _is_local_openai_compatible_base(api_base: str) -> bool:
    if not api_base:
        return False
    try:
        parsed = urlsplit(api_base)
    except ValueError:
        return False
    host = (parsed.hostname or "").lower()
    if host not in {"127.0.0.1", "localhost", "::1"}:
        return False
    path = (parsed.path or "").rstrip("/")
    return not path or path.endswith("/v1")


def _first_non_empty(*values: str | None) -> str:
    for value in values:
        if value:
            return value
    return ""


def apply_openhands_llm_env(env: dict[str, str]) -> dict[str, str]:
    """Map FeatureLiftBench/OpenAI env vars to OpenHands LLM_* variables."""
    updated = dict(env)
    api_key = _first_non_empty(
        updated.get("OPENAI_API_KEY"),
        updated.get("FEATURELIFTBENCH_API_KEY"),
        updated.get("LLM_API_KEY"),
    )
    api_base = _first_non_empty(
        updated.get("OPENAI_BASE_URL"),
        updated.get("OPENAI_API_BASE"),
        updated.get("FEATURELIFTBENCH_API_BASE"),
        updated.get("LLM_BASE_URL"),
    )
    if api_key:
        updated.setdefault("LLM_API_KEY", api_key)
    if api_base:
        updated.setdefault("LLM_BASE_URL", api_base)
    model = _first_non_empty(updated.get("FEATURELIFTBENCH_MODEL"), updated.get("LLM_MODEL"))
    if model:
        # OpenHands routes through LiteLLM, which needs the provider prefix
        # (e.g. deepseek/deepseek-v4-flash). Do not strip deepseek/ here.
        updated.setdefault("LLM_MODEL", model)
    return updated
