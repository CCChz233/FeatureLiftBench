#!/usr/bin/env python3
"""Diagnose TD-Cognition missing_submission on compare suite."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path("experiments/methods/ablation/compare-20260728-155516/td_cognition")


def analyze(task: str) -> dict:
    p = ROOT / task
    ws = p / "workspace"
    ev = p / "agent" / "openhands_events.jsonl"
    out: dict = {"task": task}

    sub_ws = ws / "submission"
    if sub_ws.is_file():
        out["ws_submission"] = "LOCKED_FILE" if "LOCKED" in sub_ws.read_text()[:80] else "FILE"
    elif sub_ws.is_dir():
        out["ws_submission"] = "DIR:" + ",".join(sorted(x.name for x in sub_ws.iterdir())[:8])
    else:
        out["ws_submission"] = "MISSING"

    cog = ws / "COGNITION.md"
    out["cognition_bytes"] = cog.stat().st_size if cog.exists() else 0
    if cog.exists():
        text = cog.read_text()
        out["cognition_still_template"] = "1. ..." in text and "## Critical Use Cases" in text
        out["use_case_numbered"] = len(re.findall(r"(?m)^\s*\d+\.\s+\S+", text))

    probes = []
    if (ws / "probes").is_dir():
        probes = [
            str(x.relative_to(ws))
            for x in (ws / "probes").rglob("*.py")
            if x.name != "__init__.py"
        ]
    out["probe_py"] = probes
    out["gate"] = (ws / "td_cognition_gate.json").exists()

    prompt = p / "agent" / "openhands_task.md"
    if prompt.exists():
        pt = prompt.read_text()
        out["prompt_has_td_gate"] = "TD-Cognition" in pt or "unlock_submission" in pt

    if not ev.exists():
        out["events"] = 0
        return out

    lines = ev.read_text(errors="replace").splitlines()
    out["events"] = len(lines)
    unlock_runs = []
    pytest_probes = 0
    sub_write_attempts = 0
    terminal_errors = []
    for i, line in enumerate(lines):
        try:
            obj = json.loads(line)
        except Exception:
            continue
        tool = obj.get("tool_name") or ""
        action = obj.get("action") if isinstance(obj.get("action"), dict) else {}
        path = str(action.get("path") or "")
        cmd = str(action.get("command") or "")
        tc = obj.get("tool_call") if isinstance(obj.get("tool_call"), dict) else {}
        fn = tc.get("function") if isinstance(tc.get("function"), dict) else {}
        args_raw = fn.get("arguments")
        if isinstance(args_raw, str):
            try:
                args = json.loads(args_raw)
            except Exception:
                args = {}
        elif isinstance(args_raw, dict):
            args = args_raw
        else:
            args = {}
        shell = str(args.get("command") or (cmd if tool == "terminal" else "") or "")
        if tool == "terminal" and "unlock_submission" in shell:
            unlock_runs.append({"i": i, "cmd": shell[:200]})
        if tool == "terminal" and "pytest" in shell and "probe" in shell:
            pytest_probes += 1
        if tool == "file_editor" and "submission" in path and cmd in {
            "create",
            "write",
            "str_replace",
            "insert",
        }:
            sub_write_attempts += 1
        if obj.get("kind") == "AgentErrorEvent" or obj.get("error"):
            err = str(obj.get("error") or "")[:180]
            if "submission" in err.lower() or "locked" in err.lower() or "is a file" in err.lower():
                terminal_errors.append(err)

    out["unlock_runs"] = len(unlock_runs)
    out["unlock_samples"] = unlock_runs[:3]
    out["pytest_probes"] = pytest_probes
    out["sub_write_attempts"] = sub_write_attempts
    out["submission_path_errors"] = terminal_errors[:5]

    # Did agent finish while still locked?
    out["mentions_unlock_in_text"] = sum(1 for L in lines if "unlock_submission" in L.lower())
    return out


def main() -> None:
    rows = [analyze(p.name) for p in sorted(ROOT.iterdir()) if p.is_dir()]
    print(f"n={len(rows)}")
    for r in rows:
        print(
            f"{r['task']}: ws={r.get('ws_submission')} cog_bytes={r.get('cognition_bytes')} "
            f"template={r.get('cognition_still_template')} probes={r.get('probe_py')} "
            f"gate={r.get('gate')} unlock_runs={r.get('unlock_runs')} "
            f"sub_writes={r.get('sub_write_attempts')} events={r.get('events')} "
            f"prompt_td={r.get('prompt_has_td_gate')}"
        )
        if r.get("unlock_samples"):
            print("  unlock:", r["unlock_samples"])
        if r.get("submission_path_errors"):
            print("  errs:", r["submission_path_errors"])
    print("---AGG---")
    print("locked_file", sum(r.get("ws_submission") == "LOCKED_FILE" for r in rows))
    print("prompt_td", sum(bool(r.get("prompt_has_td_gate")) for r in rows))
    print("still_template", sum(bool(r.get("cognition_still_template")) for r in rows))
    print("has_probes", sum(1 for r in rows if r.get("probe_py")))
    print("any_unlock", sum(r.get("unlock_runs", 0) > 0 for r in rows))
    print("any_gate", sum(bool(r.get("gate")) for r in rows))


if __name__ == "__main__":
    main()
