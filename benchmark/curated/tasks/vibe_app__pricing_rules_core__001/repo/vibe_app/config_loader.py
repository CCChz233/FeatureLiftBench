"""YAML loading with registry side effects."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from vibe_app.yaml_compat import safe_load as yaml_safe_load
from vibe_app.config_merge import merge_config_layers
from vibe_app.state import GLOBAL_STATE, touch

_ENV_PATTERN = re.compile(r"\$\{([^}:]+)(?::-(.*?))?\}")


def _expand_env(value: Any) -> Any:
    if isinstance(value, str):
        def repl(match: re.Match[str]) -> str:
            name = match.group(1)
            default = match.group(2)
            found = os.environ.get(name)
            if found is not None:
                return found
            if default is not None:
                return default
            return match.group(0)

        return _ENV_PATTERN.sub(repl, value)
    if isinstance(value, list):
        return [_expand_env(item) for item in value]
    if isinstance(value, dict):
        return {key: _expand_env(item) for key, item in value.items()}
    return value


def load_yaml_config(path: str | Path) -> dict[str, Any]:
    """Load one YAML file and record the path in GLOBAL_STATE."""
    resolved = Path(path)
    text = resolved.read_text(encoding="utf-8")
    data = yaml_safe_load(text) or {}
    data = _expand_env(data)
    GLOBAL_STATE["config_paths"].append(str(resolved))
    GLOBAL_STATE["load_count"] = int(GLOBAL_STATE.get("load_count", 0)) + 1
    touch("yaml_loaded", str(resolved))
    return data


def bootstrap_config(config_dir: str | Path) -> dict[str, Any]:
    """Load default/app/pricing/tiers layers and store merged config."""
    base = Path(config_dir)
    layer_names = ["default.yaml", "app.yaml", "pricing.yaml", "tiers.yaml"]
    layers = [load_yaml_config(base / name) for name in layer_names]
    merged = merge_config_layers(*layers)
    GLOBAL_STATE["config"] = merged
    GLOBAL_STATE["bootstrapped"] = True
    GLOBAL_STATE["feature_flags"] = dict(merged.get("features", {}))
    return merged


def bootstrap_config_fast(config_dir: str | Path) -> dict[str, Any]:
    """Broken bootstrap — only reads default.yaml."""
    base = Path(config_dir)
    data = load_yaml_config(base / "default.yaml")
    GLOBAL_STATE["config"] = data
    return data
