"""Parse OpenHands JSONL event logs into FeatureLiftBench usage artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CONTEXT_WINDOW_TOKENS = 131_072
RESERVED_OUTPUT_TOKENS = 8192
MAX_ALLOWED_PROMPT_TOKENS = 122_880

DEFAULT_EVENTS_FILENAME = "openhands_events.jsonl"
DEFAULT_USAGE_FILENAME = "openhands_usage.json"
DEFAULT_STDOUT_LOG_FILENAME = "openhands_stdout.log"


@dataclass(frozen=True)
class OpenHandsProgressSnapshot:
    status: str
    event_count: int
    total_tokens: int | None


def parse_openhands_progress_snapshot(log_path: Path) -> OpenHandsProgressSnapshot | None:
    """Extract live suite progress from an OpenHands JSONL stdout log."""
    if not log_path.is_file():
        return None

    event_count = 0
    total_tokens = 0
    saw_tokens = False
    last_label = ""
    try:
        events = _iter_json_events(log_path)
        for event in events:
            event_count += 1
            last_label = _openhands_event_label(event)
            for usage in _iter_usage_records(event):
                prompt = _int_metric(usage.get("prompt_tokens"))
                completion = _int_metric(usage.get("completion_tokens"))
                total = _int_metric(usage.get("total_tokens"))
                if prompt is not None:
                    total_tokens += prompt
                    saw_tokens = True
                if completion is not None:
                    total_tokens += completion
                    saw_tokens = True
                if total is not None and prompt is None and completion is None:
                    total_tokens += total
                    saw_tokens = True
    except OSError:
        return None

    if event_count <= 0:
        return None
    label = last_label or "agent"
    return OpenHandsProgressSnapshot(
        status=f"Event {event_count} · {label}",
        event_count=event_count,
        total_tokens=total_tokens if saw_tokens else None,
    )


def _openhands_event_label(event: dict[str, Any]) -> str:
    source = str(event.get("source") or "").strip()
    if source == "environment":
        tool_name = event.get("tool_name")
        if isinstance(tool_name, str) and tool_name:
            return tool_name
    if source == "agent":
        action = event.get("action")
        if isinstance(action, dict):
            command = action.get("command")
            if isinstance(command, str) and command.strip():
                return command.strip().split()[0]
    if source:
        return source
    event_type = str(event.get("type") or event.get("event") or "").strip()
    return event_type or "event"


def resolve_events_path(
    agent_output_dir: Path,
    *,
    stdout_log: Path | None = None,
) -> Path | None:
    """Pick the best JSONL source: dedicated events file, then stdout capture."""
    events_path = agent_output_dir / DEFAULT_EVENTS_FILENAME
    if events_path.is_file() and events_path.stat().st_size > 0:
        return events_path
    stdout_path = stdout_log or (agent_output_dir / DEFAULT_STDOUT_LOG_FILENAME)
    if stdout_path.is_file() and stdout_path.stat().st_size > 0:
        return stdout_path
    return None


def parse_events_jsonl(path: Path) -> dict[str, Any]:
    """Aggregate token usage from an OpenHands --json JSONL file."""
    if not path.is_file():
        return _empty_usage(unverified=True, reason="events_file_missing")

    prompt_tokens = 0
    completion_tokens = 0
    api_calls = 0
    assistant_steps = 0
    max_prompt_tokens_per_call = 0
    max_total_tokens_per_call = 0
    saw_usage = False

    try:
        events = _iter_json_events(path)
        for event in events:
            for usage in _iter_usage_records(event):
                saw_usage = True
                prompt = _int_metric(usage.get("prompt_tokens"))
                completion = _int_metric(usage.get("completion_tokens"))
                total = _int_metric(usage.get("total_tokens"))
                if prompt is not None:
                    prompt_tokens += prompt
                    max_prompt_tokens_per_call = max(max_prompt_tokens_per_call, prompt)
                if completion is not None:
                    completion_tokens += completion
                if total is not None:
                    max_total_tokens_per_call = max(max_total_tokens_per_call, total)
                elif prompt is not None or completion is not None:
                    call_total = (prompt or 0) + (completion or 0)
                    max_total_tokens_per_call = max(max_total_tokens_per_call, call_total)
                api_calls += 1

            if _looks_like_assistant_step(event):
                assistant_steps += 1
    except OSError:
        return _empty_usage(unverified=True, reason="events_file_unreadable")

    if not saw_usage:
        return _empty_usage(unverified=True, reason="no_usage_in_events")

    if max_prompt_tokens_per_call == 0 and prompt_tokens > 0:
        max_prompt_tokens_per_call = prompt_tokens
    if max_total_tokens_per_call == 0:
        max_total_tokens_per_call = prompt_tokens + completion_tokens

    context_violation = max_prompt_tokens_per_call > MAX_ALLOWED_PROMPT_TOKENS
    return {
        "assistant_steps": assistant_steps,
        "api_calls": api_calls,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "context_audit": {
            "available": True,
            "runtime": "openhands",
            "history_policy": "external_openhands",
            "token_source": "openhands_jsonl",
            "usage_unverified": False,
            "context_window_tokens": CONTEXT_WINDOW_TOKENS,
            "reserved_output_tokens": RESERVED_OUTPUT_TOKENS,
            "max_allowed_prompt_tokens": MAX_ALLOWED_PROMPT_TOKENS,
            "max_prompt_tokens_per_call": max_prompt_tokens_per_call,
            "max_total_tokens_per_call": max_total_tokens_per_call,
            "context_violation": context_violation,
            "over_context_behavior": "managed_by_openhands",
        },
    }


def write_usage_from_events(
    events_path: Path,
    output_path: Path,
) -> dict[str, Any] | None:
    """Parse JSONL and write ``openhands_usage.json`` when usage is found."""
    usage = parse_events_jsonl(events_path)
    context_audit = usage.get("context_audit")
    if not isinstance(context_audit, dict):
        return None
    if context_audit.get("usage_unverified"):
        return None
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(usage, indent=2, sort_keys=True), encoding="utf-8")
    return usage


def _empty_usage(*, unverified: bool, reason: str) -> dict[str, Any]:
    return {
        "assistant_steps": 0,
        "api_calls": 0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "context_audit": {
            "available": False,
            "runtime": "openhands",
            "history_policy": "external_openhands",
            "token_source": reason,
            "usage_unverified": unverified,
            "context_window_tokens": CONTEXT_WINDOW_TOKENS,
            "reserved_output_tokens": RESERVED_OUTPUT_TOKENS,
            "max_allowed_prompt_tokens": MAX_ALLOWED_PROMPT_TOKENS,
            "over_context_behavior": "managed_by_openhands",
        },
    }


def _iter_json_events(path: Path):
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or not stripped.startswith("{"):
                continue
            try:
                event = json.loads(stripped)
            except json.JSONDecodeError:
                continue
            if isinstance(event, dict):
                yield event


def _iter_usage_records(event: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for key in ("usage", "token_usage", "metrics"):
        nested = event.get(key)
        if isinstance(nested, dict) and _has_token_fields(nested):
            records.append(nested)
    message = event.get("message")
    if isinstance(message, dict):
        nested = message.get("usage")
        if isinstance(nested, dict) and _has_token_fields(nested):
            records.append(nested)
    llm_metrics = event.get("llm_metrics")
    if isinstance(llm_metrics, dict):
        for value in llm_metrics.values():
            if isinstance(value, dict) and _has_token_fields(value):
                records.append(value)
    data = event.get("data")
    if isinstance(data, dict):
        nested = data.get("usage")
        if isinstance(nested, dict) and _has_token_fields(nested):
            records.append(nested)
    return records


def _has_token_fields(record: dict[str, Any]) -> bool:
    return any(
        _int_metric(record.get(key)) is not None
        for key in ("prompt_tokens", "completion_tokens", "total_tokens")
    )


def _looks_like_assistant_step(event: dict[str, Any]) -> bool:
    event_type = str(event.get("type") or event.get("event") or "").lower()
    role = str(event.get("role") or "").lower()
    if role == "assistant":
        return True
    return any(marker in event_type for marker in ("assistant", "agent", "action", "message"))


def _int_metric(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value >= 0 else None
    if isinstance(value, float) and value >= 0 and value.is_integer():
        return int(value)
    if isinstance(value, str):
        try:
            parsed = int(value.strip())
        except ValueError:
            return None
        return parsed if parsed >= 0 else None
    return None
