"""Minimal YAML subset loader for simple config files (no PyYAML required)."""

from __future__ import annotations

from typing import Any


def safe_load(text: str) -> Any:
    lines = [line.rstrip() for line in text.splitlines()]
    while lines and (not lines[0].strip() or lines[0].lstrip().startswith("#")):
        lines.pop(0)
    if not lines:
        return {}
    value, _ = _parse_value(lines, 0, _indent(lines[0]))
    return value


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _parse_value(lines: list[str], index: int, indent: int) -> tuple[Any, int]:
    line = lines[index]
    stripped = line.strip()
    if stripped.startswith("- "):
        return _parse_list(lines, index, indent)
    return _parse_mapping(lines, index, indent)


def _parse_mapping(lines: list[str], index: int, indent: int) -> tuple[dict[str, Any], int]:
    mapping: dict[str, Any] = {}
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        if _indent(line) < indent:
            break
        if _indent(line) > indent:
            break
        if line.strip().startswith("- "):
            break
        key, rest = _split_key_value(line.strip())
        index += 1
        if rest is not None:
            mapping[key] = _parse_scalar(rest)
            continue
        if index >= len(lines) or _indent(lines[index]) <= indent:
            mapping[key] = {}
            continue
        child, index = _parse_value(lines, index, _indent(lines[index]))
        mapping[key] = child
    return mapping, index


def _parse_list(lines: list[str], index: int, indent: int) -> tuple[list[Any], int]:
    items: list[Any] = []
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        if _indent(line) < indent or not line.strip().startswith("- "):
            break
        payload = line.strip()[2:].strip()
        index += 1
        if payload:
            if ":" in payload:
                key, rest = _split_key_value(payload)
                item: dict[str, Any] = {key: _parse_scalar(rest) if rest is not None else {}}
                while index < len(lines) and _indent(lines[index]) > indent:
                    subline = lines[index]
                    if subline.strip().startswith("- "):
                        break
                    sub_key, sub_rest = _split_key_value(subline.strip())
                    index += 1
                    if sub_rest is not None:
                        item[sub_key] = _parse_scalar(sub_rest)
                    elif index < len(lines) and _indent(lines[index]) > _indent(subline):
                        nested, index = _parse_value(lines, index, _indent(lines[index]))
                        item[sub_key] = nested
                    else:
                        item[sub_key] = {}
                items.append(item)
            else:
                items.append(_parse_scalar(payload))
            continue
        if index < len(lines) and _indent(lines[index]) > indent:
            child, index = _parse_value(lines, index, _indent(lines[index]))
            items.append(child)
        else:
            items.append({})
    return items, index


def _split_key_value(text: str) -> tuple[str, str | None]:
    key, sep, rest = text.partition(":")
    if not sep:
        return text, None
    rest = rest.strip()
    return key.strip(), rest if rest else None


def _parse_scalar(value: str) -> Any:
    lowered = value.lower()
    if lowered in {"true", "yes"}:
        return True
    if lowered in {"false", "no"}:
        return False
    if lowered in {"null", "~"}:
        return None
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value
