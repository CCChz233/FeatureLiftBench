#!/usr/bin/env python3
"""Audit baseline trajectories against TD-Cognition behavioral hypotheses."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path("experiments/methods/ablation/compare-20260728-155516/main")


def tasks() -> list[str]:
    return sorted(
        p.name
        for p in ROOT.iterdir()
        if p.is_dir() and (p / "eval" / "result.json").exists()
    )


def eval_summary(task: str) -> dict:
    r = json.loads((ROOT / task / "eval" / "result.json").read_text())
    return {
        "status": r.get("status"),
        "build": r.get("build_pass"),
        "public": r.get("public_tests_pass"),
        "hidden": r.get("hidden_tests_pass"),
        "iso": r.get("isolation_pass"),
        "gate": (r.get("scores") or {}).get("functional_gate"),
        "extraction": (r.get("scores") or {}).get("extraction_ratio"),
    }


def reasoning_text(obj: dict) -> str:
    chunks: list[str] = []
    rc = obj.get("reasoning_content")
    if isinstance(rc, str):
        chunks.append(rc)
    thought = obj.get("thought")
    if isinstance(thought, list):
        for part in thought:
            if isinstance(part, dict) and isinstance(part.get("text"), str):
                chunks.append(part["text"])
    return "\n".join(chunks)


def analyze(task: str) -> dict:
    path = ROOT / task / "agent" / "openhands_events.jsonl"
    lines = path.read_text(errors="replace").splitlines()
    steps: list[dict] = []
    first_repo_view = None
    first_sub_write = None
    first_pytest = None
    pytest_before = 0
    pytest_after = 0
    closure_planish = 0
    self_test_planish = 0

    for i, line in enumerate(lines):
        try:
            obj = json.loads(line)
        except Exception:
            continue
        tool = obj.get("tool_name") or ""
        action = obj.get("action") if isinstance(obj.get("action"), dict) else {}
        cmd = str(action.get("command") or "")
        pth = str(action.get("path") or "")
        # terminal commands live under different kinds sometimes
        shell_cmd = ""
        if tool in {"terminal", "run", "execute_bash", "bash"}:
            shell_cmd = str(action.get("command") or action.get("cmd") or "")
        # some events put command in tool_call
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
        if not shell_cmd and isinstance(args.get("command"), str):
            shell_cmd = args["command"]
        if not pth and isinstance(args.get("path"), str):
            pth = args["path"]
        if not cmd and isinstance(args.get("command"), str) and tool == "file_editor":
            cmd = args["command"]

        reason = reasoning_text(obj).lower()
        if any(
            k in reason
            for k in (
                "closure plan",
                "required surface",
                "use case",
                "before implementing",
                "before editing",
                "contract",
            )
        ):
            closure_planish += 1
        if any(k in reason for k in ("write a test", "self-test", "probe", "pytest")):
            self_test_planish += 1

        kind = None
        detail = ""
        if tool == "file_editor":
            kind = f"file_editor:{cmd or '?'}"
            detail = pth
            if "/repo" in pth or pth.endswith("/repo") or "/repo/" in pth:
                if cmd in {"view", "read", ""} and first_repo_view is None:
                    first_repo_view = i
            if "/submission" in pth and cmd in {"create", "write", "str_replace", "insert", "undo_edit"}:
                if first_sub_write is None:
                    first_sub_write = i
                kind = f"SUB_EDIT:{cmd}"
            elif "/submission" in pth and cmd == "view":
                kind = "sub_view"
        elif tool in {"terminal", "run", "execute_bash", "bash"} or shell_cmd:
            kind = "shell"
            detail = shell_cmd[:200]
            if "pytest" in shell_cmd:
                kind = "PYTEST"
                if first_pytest is None:
                    first_pytest = i
                if first_sub_write is None:
                    pytest_before += 1
                else:
                    pytest_after += 1
        elif tool:
            kind = tool
            detail = (cmd or pth or shell_cmd)[:120]

        if kind:
            steps.append({"i": i, "kind": kind, "detail": detail[:160]})

    sub_edits = [s for s in steps if s["kind"].startswith("SUB_EDIT")]
    pytests = [s for s in steps if s["kind"] == "PYTEST"]
    return {
        "n_events": len(lines),
        "eval": eval_summary(task),
        "first_repo_view": first_repo_view,
        "first_sub_write": first_sub_write,
        "first_pytest": first_pytest,
        "n_sub_edits": len(sub_edits),
        "n_pytest": len(pytests),
        "pytest_before_first_edit": pytest_before,
        "pytest_after_first_edit": pytest_after,
        "closureish_reason_hits": closure_planish,
        "selftestish_reason_hits": self_test_planish,
        "timeline_head": steps[:20],
        "around_first_edit": [
            s
            for s in steps
            if first_sub_write is not None and abs(s["i"] - first_sub_write) <= 5
        ],
        "pytest_cmds": [s["detail"] for s in pytests[:8]],
    }


def main() -> None:
    done = tasks()
    print(f"completed_with_eval={len(done)} root={ROOT}")
    for task in done:
        print("=" * 72)
        print(task)
        print(json.dumps(analyze(task), indent=2, ensure_ascii=False)[:5000])


if __name__ == "__main__":
    main()
