from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

_SENSITIVE_KEY = re.compile(r"(?:api[_-]?key|authorization|password|secret|token)$", re.IGNORECASE)
_PRIVATE_TEXT = re.compile(
    r"(?:hidden_tests|reference_solution|(?:^|[/\\])evaluation[/\\]|(?:^|[/\\])eval[/\\]result\.json)",
    re.IGNORECASE,
)
_ABSOLUTE_PATH = re.compile(r"/(?:Users|home|private|tmp|var)/[^\s\"']+")
_BULKY_KEYS = frozenset(
    {
        "critic_result",
        "file_text",
        "full_output_save_dir",
        "llm_response_id",
        "new_content",
        "old_content",
        "reasoning_content",
        "responses_reasoning_item",
        "thinking_blocks",
        "tool_call",
    }
)
_LONG_STRING_KEYS = frozenset({"summary", "thought"})
_MAX_STRING_CHARS = 500
_MAX_LONG_STRING_CHARS = 800


def bounded_trace_excerpt(events_path: Path, *, max_events: int, max_chars: int) -> dict[str, Any]:
    if not events_path.is_file():
        return {"available": False, "events": [], "source_event_count": 0, "truncated": False}
    lines = [line for line in events_path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()]
    selected = lines[-max_events:]
    rendered: list[Any] = []
    used = 0
    for line in selected:
        try:
            value: Any = json.loads(line)
        except json.JSONDecodeError:
            value = {"raw": line}
        sanitized = _compact(_sanitize(value))
        text = json.dumps(sanitized, ensure_ascii=False, sort_keys=True)
        remaining = max_chars - used
        if remaining <= 0:
            break
        if len(text) > remaining:
            rendered.append({"truncated_event": text[:remaining]})
            used = max_chars
            break
        rendered.append(sanitized)
        used += len(text)
    return {
        "available": True,
        "events": rendered,
        "source_event_count": len(lines),
        "selected_event_count": len(rendered),
        "truncated": len(lines) > len(selected) or len(rendered) < len(selected),
    }


def _sanitize(value: Any, *, key: str = "") -> Any:
    if _SENSITIVE_KEY.search(key):
        return "[REDACTED_SECRET]"
    if isinstance(value, Mapping):
        return {str(item_key): _sanitize(item, key=str(item_key)) for item_key, item in value.items()}
    if isinstance(value, list):
        return [_sanitize(item, key=key) for item in value]
    if isinstance(value, str):
        text = _PRIVATE_TEXT.sub("[REDACTED_PRIVATE_BOUNDARY]", value)
        return _ABSOLUTE_PATH.sub("[REDACTED_ABSOLUTE_PATH]", text)
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return str(value)


def _compact(value: Any, *, key: str = "") -> Any:
    if isinstance(value, Mapping):
        compacted: dict[str, Any] = {}
        for item_key, item in value.items():
            name = str(item_key)
            if name in _BULKY_KEYS:
                continue
            compacted[name] = _compact(item, key=name)
        return compacted
    if isinstance(value, list):
        return [_compact(item, key=key) for item in value]
    if isinstance(value, str):
        limit = _MAX_LONG_STRING_CHARS if key in _LONG_STRING_KEYS else _MAX_STRING_CHARS
        if len(value) > limit:
            return value[:limit] + "...[truncated]"
        return value
    return value

