#!/usr/bin/env python3
"""Pilot health + trajectory audit for compare suite main/td arms."""
from __future__ import annotations

import json
from pathlib import Path

COMPARE = Path("experiments/ablation/compare-20260728-155516")


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


def parse_tool(obj: dict) -> tuple[str, str, str]:
    tool = str(obj.get("tool_name") or "")
    action = obj.get("action") if isinstance(obj.get("action"), dict) else {}
    cmd = str(action.get("command") or "")
    pth = str(action.get("path") or "")
    shell = ""
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
    if tool in {"terminal", "run", "execute_bash", "bash"}:
        shell = str(action.get("command") or action.get("cmd") or args.get("command") or "")
    if not pth and isinstance(args.get("path"), str):
        pth = args["path"]
    if not cmd and tool == "file_editor" and isinstance(args.get("command"), str):
        cmd = args["command"]
    if not shell and isinstance(args.get("command"), str) and tool == "terminal":
        shell = args["command"]
    return tool, cmd, pth or shell


def analyze_task(arm_dir: Path, task: str) -> dict:
    root = arm_dir / task
    out: dict = {"task": task}
    eval_path = root / "eval" / "result.json"
    if eval_path.exists():
        r = json.loads(eval_path.read_text())
        out["eval"] = {
            "status": r.get("status"),
            "build": r.get("build_pass"),
            "public": r.get("public_tests_pass"),
            "hidden": r.get("hidden_tests_pass"),
            "iso": r.get("isolation_pass"),
            "gate": (r.get("scores") or {}).get("functional_gate"),
            "extraction": (r.get("scores") or {}).get("extraction_ratio"),
        }
    else:
        out["eval"] = None

    usage = root / "agent" / "openhands_usage.json"
    if usage.exists():
        u = json.loads(usage.read_text())
        out["usage"] = {
            k: u.get(k)
            for k in (
                "total_tokens",
                "prompt_tokens",
                "completion_tokens",
                "api_calls",
                "elapsed_seconds",
                "exit_status",
            )
            if k in u or True
        }
        # keep compact
        out["usage"] = {k: v for k, v in out["usage"].items() if v is not None}

    events = root / "agent" / "openhands_events.jsonl"
    if not events.exists():
        out["events"] = None
        return out

    first_repo = first_sub = first_pytest = None
    n_sub = n_pytest = pytest_before = pytest_after = 0
    agent_errors = 0
    finish = 0
    n = 0
    for i, line in enumerate(events.open()):
        n += 1
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if obj.get("kind") == "AgentErrorEvent" or obj.get("error"):
            agent_errors += 1
        tool, cmd, detail = parse_tool(obj)
        low = (detail or "").lower()
        if tool == "finish":
            finish += 1
        if tool == "file_editor":
            if first_repo is None and "/repo" in low:
                first_repo = i
            if "/submission" in low and cmd in {
                "create",
                "write",
                "str_replace",
                "insert",
                "undo_edit",
            }:
                n_sub += 1
                if first_sub is None:
                    first_sub = i
        if tool == "terminal" and "pytest" in low:
            n_pytest += 1
            if first_pytest is None:
                first_pytest = i
            if first_sub is None:
                pytest_before += 1
            else:
                pytest_after += 1
        # mkdir submission counts as engagement
        if tool == "terminal" and "mkdir" in low and "submission" in low and first_sub is None:
            # treat nearby as pre-edit setup; don't set first_sub
            pass
        reason = reasoning_text(obj).lower()
        if "pytest" in low and tool == "terminal":
            pass

    out["traj"] = {
        "n_events": n,
        "first_repo": first_repo,
        "first_sub_edit": first_sub,
        "first_pytest": first_pytest,
        "n_sub_edits": n_sub,
        "n_pytest": n_pytest,
        "pytest_before_edit": pytest_before,
        "pytest_after_edit": pytest_after,
        "agent_error_events": agent_errors,
        "finish_events": finish,
        "has_submission_dir": (root / "submission" / "featurelifted").exists()
        or (root / "workspace" / "submission" / "featurelifted").exists(),
    }
    # find submission package under common layouts
    for cand in [
        root / "submission" / "featurelifted",
        root / "workspace" / "submission" / "featurelifted",
        root / "agent_workspace" / "submission" / "featurelifted",
    ]:
        if cand.exists():
            out["traj"]["submission_pkg"] = str(cand.relative_to(root))
            break
    # search
    pkgs = list(root.rglob("featurelifted/__init__.py"))
    if pkgs:
        out["traj"]["submission_pkg"] = str(pkgs[0].relative_to(root))
    return out


def main() -> None:
    for arm in ("main", "td_cognition"):
        arm_dir = COMPARE / arm
        if not arm_dir.exists():
            print(f"ARM {arm}: not started")
            continue
        tasks = sorted(
            p.name
            for p in arm_dir.iterdir()
            if p.is_dir() and not p.name.startswith(".")
        )
        print("=" * 72)
        print(f"ARM {arm}: {len(tasks)} task dirs")
        rows = []
        for task in tasks:
            rows.append(analyze_task(arm_dir, task))
        done = [r for r in rows if r.get("eval")]
        running = [r for r in rows if not r.get("eval")]
        passed = [r for r in done if r["eval"].get("status") == "passed" or r["eval"].get("gate") == 1.0]
        print(f"eval_done={len(done)} running_or_pending={len(running)} passed={len(passed)}")
        for r in rows:
            e = r.get("eval") or {}
            t = r.get("traj") or {}
            print(
                f"- {r['task']}: status={e.get('status', 'RUNNING')} "
                f"B/P/H/I={e.get('build')}/{e.get('public')}/{e.get('hidden')}/{e.get('iso')} "
                f"ext={e.get('extraction')} "
                f"events={t.get('n_events')} repo@{t.get('first_repo')} "
                f"edit@{t.get('first_sub_edit')} pytest={t.get('n_pytest')} "
                f"(before={t.get('pytest_before_edit')},after={t.get('pytest_after_edit')}) "
                f"errs={t.get('agent_error_events')}"
            )
        # aggregate pattern
        if done:
            edits = [r["traj"]["first_sub_edit"] for r in done if r.get("traj") and r["traj"].get("first_sub_edit") is not None]
            repos = [r["traj"]["first_repo"] for r in done if r.get("traj") and r["traj"].get("first_repo") is not None]
            pytest_any = sum(1 for r in done if (r.get("traj") or {}).get("n_pytest", 0) > 0)
            pytest_before_any = sum(1 for r in done if (r.get("traj") or {}).get("pytest_before_edit", 0) > 0)
            print(
                "AGG:",
                f"medianish_repo={sorted(repos)[len(repos)//2] if repos else None}",
                f"medianish_edit={sorted(edits)[len(edits)//2] if edits else None}",
                f"tasks_with_pytest={pytest_any}/{len(done)}",
                f"tasks_pytest_before_edit={pytest_before_any}/{len(done)}",
            )


if __name__ == "__main__":
    main()
