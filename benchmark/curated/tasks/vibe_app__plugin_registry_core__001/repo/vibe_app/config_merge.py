"""Deep merge helpers for layered YAML config."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


def _is_mapping(value: Any) -> bool:
    return isinstance(value, dict)


def merge_config_layers(*layers: dict[str, Any]) -> dict[str, Any]:
    """Deep-merge config dicts; later layers override earlier keys."""
    result: dict[str, Any] = {}
    for layer in layers:
        if not layer:
            continue
        result = _deep_merge(result, layer)
    return result


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in overlay.items():
        if key in merged and _is_mapping(merged[key]) and _is_mapping(value):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def merge_config_layers_shallow(*layers: dict[str, Any]) -> dict[str, Any]:
    """Legacy shallow merge — wrong for nested overrides."""
    result: dict[str, Any] = {}
    for layer in layers:
        result.update(layer)
    return result
