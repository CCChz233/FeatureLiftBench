#!/usr/bin/env python3
"""Phase-0 token-utility scan: when did submission/featurelifted last change?

Does not re-evaluate intermediate snapshots. Gold for "earliest sufficient
snapshot" is a later phase. This only measures the last package-mutating write
against billed tokens from context_audit.jsonl.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PACKAGE_MARKERS = ("/submission/featurelifted/", "submission/featurelifted/")
WRITE_EDITOR_COMMANDS = frozenset({"create", "str_replace", "insert", "write", "edit"})
FRAC_BINS = [(0.0, 0.50), (0.50, 0.70), (0.70, 0.85), (0.85, 0.95), (0.95, 1.01)]
TOKEN_BINS = [
    (0, 1_000_000),
    (1_000_000, 2_000_000),
    (2_000_000, 3_000_000),
    (3_000_000, 10**12),
]


def _parse_ts(value: Any) -> float | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        parsed = datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.timestamp()
    except ValueError:
        return None


def _quantile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    pos = (len(ordered) - 1) * p
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi:
        return float(ordered[lo])
    return float(ordered[lo] + (ordered[hi] - ordered[lo]) * (pos - lo))


def _summarize(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"n": 0, "mean": None, "median": None, "p10": None, "p90": None}
    return {
        "n": len(values),
        "mean": sum(values) / len(values),
        "median": statistics.median(values),
        "p10": _quantile(values, 0.1),
        "p90": _quantile(values, 0.9),
    }


def _bin_counts(values: list[float], bins: list[tuple[float, float]]) -> list[dict[str, Any]]:
    rows = []
    for lo, hi in bins:
        n = sum(1 for value in values if lo <= value < hi)
        rows.append({"lo": lo, "hi": hi, "n": n, "share": n / len(values) if values else 0.0})
    return rows


def load_billed_calls(audit_path: Path) -> list[tuple[float, int, int]]:
    """Return (timestamp, call_total_tokens, cumulative_after_call)."""

    calls: list[tuple[float, int]] = []
    if not audit_path.is_file():
        return []
    for line in audit_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = _parse_ts(payload.get("timestamp"))
        if ts is None:
            continue
        prompt = payload.get("prompt_tokens") or 0
        completion = payload.get("completion_tokens") or 0
        total = payload.get("total_tokens")
        if not isinstance(total, (int, float)):
            total = prompt + completion
        calls.append((ts, int(total)))
    calls.sort(key=lambda item: item[0])
    out: list[tuple[float, int, int]] = []
    cumulative = 0
    for ts, billed in calls:
        cumulative += billed
        out.append((ts, billed, cumulative))
    return out


def tokens_at(calls: list[tuple[float, int, int]], ts: float | None) -> int | None:
    if not calls or ts is None:
        return None
    last = None
    for call_ts, _billed, cumulative in calls:
        if call_ts <= ts + 1.0:
            last = cumulative
        else:
            break
    return last if last is not None else 0


def _path_blob(event: dict[str, Any]) -> str:
    action = event.get("action") if isinstance(event.get("action"), dict) else {}
    parts = [
        str(event.get("tool_name") or ""),
        str(action.get("command") or ""),
        str(action.get("path") or action.get("file_path") or action.get("file") or ""),
        str(event.get("summary") or ""),
    ]
    return " ".join(parts).replace("\\", "/")


def is_package_write(event: dict[str, Any]) -> bool:
    if str(event.get("kind") or "") != "ActionEvent":
        return False
    tool = str(event.get("tool_name") or "").strip().lower()
    action = event.get("action") if isinstance(event.get("action"), dict) else {}
    command = str(action.get("command") or "").strip().lower()
    blob = _path_blob(event)
    if not any(marker in blob for marker in PACKAGE_MARKERS):
        return False
    if tool in {"file_editor", "str_replace_editor", "edit_file", "write_file"}:
        return command in WRITE_EDITOR_COMMANDS or not command
    if tool in {"terminal", "run", "bash", "execute_bash"}:
        cmd = str(action.get("command") or "")
        return bool(
            any(
                token in cmd
                for token in ("tee ", "cat >", "python3 -c", "sed -i", "cp ", "mv ")
            )
            and "featurelifted" in cmd.replace("\\", "/")
            and "pytest" not in cmd
        )
    return False


def functional_gate(task_dir: Path) -> bool | None:
    path = task_dir / "eval" / "result.json"
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    value = (payload.get("scores") or {}).get("functional_gate")
    if value == 1.0:
        return True
    if value == 0.0:
        return False
    return None


def analyze_task(task_dir: Path) -> dict[str, Any]:
    agent = task_dir / "agent"
    events_path = agent / "openhands_events.jsonl"
    calls = load_billed_calls(agent / "context_audit.jsonl")
    total_tokens = calls[-1][2] if calls else 0
    writes: list[dict[str, Any]] = []
    action_count = 0
    if events_path.is_file():
        for line in events_path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(event, dict) or event.get("kind") != "ActionEvent":
                continue
            action_count += 1
            if not is_package_write(event):
                continue
            ts = _parse_ts(event.get("timestamp"))
            writes.append(
                {
                    "step": action_count,
                    "tokens": tokens_at(calls, ts),
                    "tool": event.get("tool_name"),
                    "command": (event.get("action") or {}).get("command")
                    if isinstance(event.get("action"), dict)
                    else None,
                    "path": (event.get("action") or {}).get("path")
                    if isinstance(event.get("action"), dict)
                    else None,
                }
            )
    last = writes[-1] if writes else None
    first = writes[0] if writes else None
    last_tokens = last["tokens"] if last else None
    first_tokens = first["tokens"] if first else None
    last_frac = (
        last_tokens / total_tokens
        if last_tokens is not None and total_tokens
        else None
    )
    first_frac = (
        first_tokens / total_tokens
        if first_tokens is not None and total_tokens
        else None
    )
    tail = (
        total_tokens - last_tokens
        if last_tokens is not None and total_tokens
        else None
    )
    passed = functional_gate(task_dir)
    return {
        "task_id": task_dir.name,
        "functional_pass": passed,
        "total_tokens": total_tokens,
        "action_count": action_count,
        "package_writes": len(writes),
        "first_write_tokens": first_tokens,
        "first_write_frac": first_frac,
        "last_write_tokens": last_tokens,
        "last_write_frac": last_frac,
        "last_write_step": last["step"] if last else None,
        "tail_tokens_after_last_write": tail,
        "last_write_after_2m": bool(last_tokens is not None and last_tokens >= 2_000_000),
        "total_after_2m": bool(total_tokens >= 2_000_000),
        "has_events": events_path.is_file(),
        "has_audit": bool(calls),
    }


def summarize_rows(rows: list[dict[str, Any]], *, label: str) -> dict[str, Any]:
    usable = [row for row in rows if row.get("last_write_frac") is not None]
    passed = [row for row in usable if row.get("functional_pass") is True]
    failed = [row for row in usable if row.get("functional_pass") is False]

    def pack(subset: list[dict[str, Any]]) -> dict[str, Any]:
        fracs = [float(row["last_write_frac"]) for row in subset]
        firsts = [float(row["first_write_frac"]) for row in subset if row.get("first_write_frac") is not None]
        tails = [
            float(row["tail_tokens_after_last_write"])
            for row in subset
            if row.get("tail_tokens_after_last_write") is not None
        ]
        lasts = [
            float(row["last_write_tokens"])
            for row in subset
            if row.get("last_write_tokens") is not None
        ]
        totals = [float(row["total_tokens"]) for row in subset]
        return {
            "n": len(subset),
            "last_write_frac": _summarize(fracs),
            "first_write_frac": _summarize(firsts),
            "tail_tokens": _summarize(tails),
            "last_write_tokens": _summarize(lasts),
            "total_tokens": _summarize(totals),
            "last_write_frac_bins": _bin_counts(fracs, FRAC_BINS),
            "last_write_token_bins": _bin_counts(lasts, TOKEN_BINS),
            "share_last_write_after_2m": (
                sum(1 for row in subset if row.get("last_write_after_2m")) / len(subset)
                if subset
                else 0.0
            ),
            "share_total_after_2m": (
                sum(1 for row in subset if row.get("total_after_2m")) / len(subset)
                if subset
                else 0.0
            ),
            "share_tail_over_20pct": (
                sum(1 for row in subset if (row.get("last_write_frac") or 1) < 0.80)
                / len(subset)
                if subset
                else 0.0
            ),
            "share_tail_under_5pct": (
                sum(1 for row in subset if (row.get("last_write_frac") or 0) >= 0.95)
                / len(subset)
                if subset
                else 0.0
            ),
        }

    return {
        "label": label,
        "assigned": len(rows),
        "with_package_write": len(usable),
        "pass": pack(passed),
        "fail": pack(failed),
        "all": pack(usable),
    }


def scan_suite(suite_dir: Path) -> dict[str, Any]:
    rows = []
    for task_dir in sorted(path for path in suite_dir.iterdir() if path.is_dir()):
        if not (task_dir / "agent").is_dir():
            continue
        rows.append(analyze_task(task_dir))
    return {
        "suite": str(suite_dir),
        "summary": summarize_rows(rows, label=suite_dir.name),
        "tasks": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("suites", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    reports = [scan_suite(path.resolve()) for path in args.suites]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"reports": reports}, indent=2) + "\n", encoding="utf-8")
    for report in reports:
        summary = report["summary"]
        print(f"== {summary['label']} ==")
        print(
            f"assigned={summary['assigned']} with_package_write={summary['with_package_write']}"
        )
        for split in ("pass", "fail"):
            block = summary[split]
            last = block["last_write_frac"]
            tail = block["tail_tokens"]
            print(
                f"  {split}: n={block['n']} last_frac median={last['median']} "
                f"p10={last['p10']} p90={last['p90']} "
                f"tail_median={tail['median']} "
                f"last_write>=2M={block['share_last_write_after_2m']:.2%} "
                f"tail>20%={block['share_tail_over_20pct']:.2%} "
                f"tail<5%={block['share_tail_under_5pct']:.2%}"
            )
            print("    frac_bins", [f"{row['lo']:.2f}-{row['hi']:.2f}:{row['n']}" for row in block["last_write_frac_bins"]])
            print(
                "    token_bins",
                [f"{int(row['lo']/1e6)}-{int(row['hi']/1e6) if row['hi']<1e11 else 'inf'}M:{row['n']}" for row in block["last_write_token_bins"]],
            )
    print("wrote", args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
