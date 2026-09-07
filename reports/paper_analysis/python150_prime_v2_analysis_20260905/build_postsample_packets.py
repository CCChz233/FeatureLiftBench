#!/usr/bin/env python3
"""Build L0 screens, stratified post-sample packets, and process-tag screens.

Does not assign root_cause_primary. Close-read labels stay in write_f3_*.py.
"""
from __future__ import annotations

import ast
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ROWS = OUT / "task_results.csv"
TASK_ROOT = ROOT / "benchmark/tasks"

SUITES = {
    "deepseek-v4-pro": ROOT / "experiments/python/openhands/deepseek-v4-pro/python150-prime-v2-main-r1",
    "deepseek-v4-flash": ROOT / "experiments/python/openhands/deepseek-v4-flash/python200-prime-v2-main-r1",
    "gpt-5.6-luna": ROOT / "experiments/python/openhands/gpt-5.6-luna/python200-prime-v2-main-r1",
    "qwen3.6-35b-a3b-fp8": ROOT / "experiments/python/openhands/qwen3.6-35b-a3b-fp8/python200-prime-v2-main-r1",
    "gpt-oss-120b": ROOT / "experiments/python/openhands/gpt-oss-120b/python200-prime-v2-main-r1",
}

POST_MODELS = ["gpt-5.6-luna", "qwen3.6-35b-a3b-fp8", "gpt-oss-120b"]
KNOWN_PUBLIC_DEFECTS = {
    "click__lazy_command_core__hard3_001",
    "pluggy__hook_wrapper_core__hard3_001",
    "hatch__project_metadata_core__hard3_001",
    "readme_renderer__content_type_core__hard3_001",
    "pytest__ini_markers_core__001",
}
SAMPLE_SEED = "python150-postsample-v1"

SKIP = {
    "True", "False", "None", "len", "set", "list", "dict", "str", "int", "bool",
    "tuple", "type", "isinstance", "hasattr", "getattr", "setattr", "print",
    "range", "enumerate", "zip", "sorted", "all", "any", "min", "max", "sum",
    "open", "Path", "pytest", "raises", "warns", "approx", "tmp_path",
    "monkeypatch", "featurelifted", "capsys", "tmpdir",
}

FAILED_RE = re.compile(r"^(FAILED|ERROR) (.+?)(?: - |$)")
NODE_RE = re.compile(r"::(\w+)(?:\[.*\])?$")
HIDDEN_LEAK = re.compile(r"hidden_tests/|test_hidden|::test_")


def sha_key(model: str, task_id: str) -> str:
    return hashlib.sha256(f"{model}|{task_id}|{SAMPLE_SEED}".encode()).hexdigest()


def required_paths(meta: dict) -> list[str]:
    out: list[str] = []

    def walk(items: object) -> None:
        if not items:
            return
        if isinstance(items, list):
            for item in items:
                walk(item)
            return
        if isinstance(items, dict):
            path = items.get("path")
            if path:
                out.append(str(path))
            walk(items.get("members"))
            return
        if isinstance(items, str):
            out.append(items)

    walk((meta.get("public_spec") or {}).get("required_api") or [])
    return out


def public_clauses(task_id: str) -> list[dict[str, str]]:
    path = TASK_ROOT / task_id / "evaluation" / "behavior_contract.json"
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for clause in data.get("public_clauses") or []:
        if isinstance(clause, dict):
            rows.append(
                {
                    "id": str(clause.get("behavior_id") or ""),
                    "kind": str(clause.get("clause_kind") or ""),
                    "text": str(clause.get("text") or "")[:400],
                }
            )
    return rows


def first_fail_nodeid(log_text: str) -> str:
    for line in log_text.splitlines():
        m = FAILED_RE.match(line.strip())
        if m:
            return m.group(2).strip()
    for line in log_text.splitlines():
        if line.startswith("____") and "test_" in line:
            return line.strip("_ ").strip()
    return ""


def redact(text: str) -> str:
    text = HIDDEN_LEAK.sub("[redacted]", text)
    text = re.sub(r"[\w./-]+::test_\w+", "[nodeid omitted]", text)
    return text


def names_in_func(src: str, func_name: str) -> list[str]:
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            for child in ast.walk(node):
                if isinstance(child, ast.Attribute):
                    names.append(child.attr)
                elif isinstance(child, ast.Name):
                    names.append(child.id)
            break
    return sorted(set(names))


def test_func_source(task_id: str, func_name: str) -> str:
    public_dir = TASK_ROOT / task_id / "public_tests"
    if not public_dir.is_dir() or not func_name:
        return ""
    for path in sorted(public_dir.rglob("*.py")):
        src = path.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == func_name:
                return ast.get_source_segment(src, node) or ""
    return ""


def error_excerpt(log_text: str, hidden: bool) -> dict[str, str]:
    lines = log_text.splitlines()
    err = ""
    e_lines = [ln for ln in lines if ln.startswith("E ") or ln.startswith("E\t")]
    if e_lines:
        err = "\n".join(e_lines[:12])
    types = []
    for token in (
        "AssertionError",
        "AttributeError",
        "TypeError",
        "ImportError",
        "ModuleNotFoundError",
        "NameError",
        "KeyError",
        "ValueError",
        "IndexError",
        "SyntaxError",
        "IndentationError",
        "Failed to import",
        "FORBIDDEN",
        "forbidden_imports",
    ):
        if token in log_text:
            types.append(token)
    text = redact(err) if hidden else err
    if hidden:
        text = re.sub(r"'[^']{0,80}'", "'[value]'", text)
        text = re.sub(r'"[^"]{0,80}"', '"[value]"', text)
    return {"error_types": ";".join(types[:6]), "excerpt": text[:1200]}


def submission_tree(run_dir: Path) -> list[str]:
    sub = run_dir / "submission"
    if not sub.is_dir():
        return []
    out = []
    for path in sorted(sub.rglob("*")):
        if path.is_file() and path.suffix in {".py", ".toml", ".cfg", ".in", ".txt", ".md"}:
            rel = str(path.relative_to(sub))
            if any(part.startswith(".") for part in path.parts):
                continue
            out.append(rel)
            if len(out) >= 80:
                break
    return out


def snippet_for_symbol(run_dir: Path, symbols: list[str]) -> list[dict[str, str]]:
    sub = run_dir / "submission"
    if not sub.is_dir() or not symbols:
        return []
    hits: list[dict[str, str]] = []
    pats = [re.compile(rf"\b{re.escape(sym)}\b") for sym in symbols[:8] if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", sym)]
    if not pats:
        return []
    for path in sorted(sub.rglob("*.py")):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = str(path.relative_to(sub))
        if "_vendor" in rel or "html5lib" in rel:
            continue
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if any(p.search(line) for p in pats) and ("def " in line or "class " in line or "import " in line):
                start = max(0, i - 2)
                end = min(len(lines), i + 18)
                hits.append({"file": rel, "around": "\n".join(lines[start:end])[:1500]})
                if len(hits) >= 6:
                    return hits
    return hits


def parse_events(path: Path) -> dict:
    if not path.is_file():
        return {"present": False}
    n_term = n_edit = n_finish = 0
    n_repo = n_probe = n_sub_edit = 0
    last_edit_i = last_probe_i = last_i = -1
    budget_hints = []
    cmds_repo_deep = False
    for i, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines()):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        last_i = i
        tn = obj.get("tool_name") or ""
        act = obj.get("action") if isinstance(obj.get("action"), dict) else {}
        cmd = str(act.get("command") or "")
        pth = str(act.get("path") or "")
        blob = cmd + " " + pth
        pth_n = pth.replace("\\", "/")
        looks_repo = (
            "/repo/" in pth_n
            or pth_n.endswith("/repo")
            or "/repo/" in cmd
            or re.search(r"(^|[\s\"'=])repo/", cmd) is not None
        )
        if looks_repo:
            n_repo += 1
            if tn == "file_editor" or re.search(r"(grep|rg|find|cat |head |sed |python |view)", blob):
                cmds_repo_deep = True
            elif n_repo >= 1:
                cmds_repo_deep = True
        if tn == "terminal":
            n_term += 1
            if re.search(r"pytest|python\s+-c|python3\s+-c|unittest", cmd):
                n_probe += 1
                last_probe_i = i
        elif tn == "file_editor":
            n_edit += 1
            last_edit_i = i
            if "submission" in pth or "featurelifted" in pth:
                n_sub_edit += 1
        elif tn == "finish":
            n_finish += 1
        low = blob.lower()
        if any(k in low for k in ("token limit", "step limit", "budget", "max iterations", "context length")):
            budget_hints.append(blob[:160])
    inspected = n_repo > 0 and cmds_repo_deep
    stale = last_edit_i >= 0 and last_probe_i >= 0 and last_edit_i > last_probe_i
    probe = n_probe > 0
    tag = "process_unknown"
    if not path.is_file():
        tag = "process_unknown"
    elif not inspected:
        tag = "scope_not_inspected"
    elif n_finish == 0 and budget_hints:
        tag = "budget_exhaustion"
    elif not probe:
        tag = "probe_not_selected"
    elif stale:
        tag = "stale_verification"
    else:
        tag = "inspected_and_probed"
    return {
        "present": True,
        "n_term": n_term,
        "n_edit": n_edit,
        "n_finish": n_finish,
        "n_repo": n_repo,
        "n_probe": n_probe,
        "n_sub_edit": n_sub_edit,
        "inspected_repo_deep": inspected,
        "stale_after_edit": stale,
        "budget_hint_n": len(budget_hints),
        "process_tag": tag,
        "last_i": last_i,
    }


def sample_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    art = [r for r in rows if r["model"] in POST_MODELS and r["artifact_fail"] == "True"]
    quota = {
        "gpt-5.6-luna": {
            "build_failure": 2,
            "public_failure": 5,
            "hidden_failure": 3,
            "isolation_failure": 1,
        },
        "qwen3.6-35b-a3b-fp8": {
            "build_failure": 2,
            "public_failure": 5,
            "hidden_failure": 3,
            "isolation_failure": 1,
        },
        "gpt-oss-120b": {
            "build_failure": 3,
            "public_failure": 5,
            "hidden_failure": 3,
            "isolation_failure": 1,
        },
    }
    forced = []
    rest: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in art:
        if row["task_id"] in KNOWN_PUBLIC_DEFECTS:
            forced.append(row)
        else:
            rest[(row["model"], row["first_failure_stage"])].append(row)
    for key in rest:
        rest[key].sort(key=lambda r: sha_key(r["model"], r["task_id"]))
    picked = list(forced)
    seen = {(r["model"], r["task_id"]) for r in picked}
    for model, q in quota.items():
        for stage, n in q.items():
            for row in rest.get((model, stage), []):
                key = (row["model"], row["task_id"])
                if key in seen:
                    continue
                picked.append(row)
                seen.add(key)
                n -= 1
                if n <= 0:
                    break
    picked.sort(key=lambda r: (r["model"], r["first_failure_stage"], r["task_id"]))
    return picked


def packet_for(row: dict[str, str]) -> dict:
    model = row["model"]
    task_id = row["task_id"]
    stage = row["first_failure_stage"]
    run_dir = SUITES[model] / task_id
    meta = json.loads((TASK_ROOT / task_id / "metadata.json").read_text(encoding="utf-8"))
    req = required_paths(meta)
    leaves = sorted({p.rsplit(".", 1)[-1] for p in req})
    log_name = {
        "public_failure": "eval/logs/public.stdout",
        "hidden_failure": "eval/logs/hidden.stdout",
        "build_failure": "eval/logs/build.stdout",
        "isolation_failure": "eval/result.json",
    }.get(stage, "eval/result.json")
    log_path = run_dir / log_name
    log_text = ""
    if log_path.is_file() and log_path.suffix != ".json":
        log_text = log_path.read_text(encoding="utf-8", errors="replace")
    nodeid = first_fail_nodeid(log_text) if stage != "isolation_failure" else ""
    func = ""
    m = NODE_RE.search(nodeid)
    if m:
        func = m.group(1)
    hidden = stage == "hidden_failure"
    excerpt = error_excerpt(log_text, hidden=hidden)
    extra: list[str] = []
    test_src = ""
    if stage == "public_failure" and func:
        test_src = test_func_source(task_id, func)
        used = names_in_func(test_src, func)
        extra = [n for n in used if n not in set(leaves) and n not in SKIP and not n.startswith("test_")]
    isolation = {}
    result_path = run_dir / "eval" / "result.json"
    if result_path.is_file():
        result = json.loads(result_path.read_text(encoding="utf-8"))
        isolation = {
            "build_pass": result.get("build_pass"),
            "public_tests_pass": result.get("public_tests_pass"),
            "hidden_tests_pass": result.get("hidden_tests_pass"),
            "isolation_pass": result.get("isolation_pass"),
            "isolation": result.get("isolation") if isinstance(result.get("isolation"), dict) else {},
            "build_reason": (result.get("build") or {}).get("reason") if isinstance(result.get("build"), dict) else "",
        }
    symbols = []
    if func:
        symbols.append(func.replace("test_", ""))
    symbols.extend(leaves[:6])
    attr_err = re.search(r"has no attribute '(\w+)'", excerpt["excerpt"])
    if attr_err:
        symbols.insert(0, attr_err.group(1))
    return {
        "model": model,
        "task_id": task_id,
        "first_failure_stage": stage,
        "hard3": row["hard3"] == "True",
        "lift_type": row.get("lift_type"),
        "feature_family": row.get("feature_family"),
        "known_public_defect_task": task_id in KNOWN_PUBLIC_DEFECTS,
        "required_api": req,
        "required_leaves": leaves,
        "public_clauses": public_clauses(task_id),
        "first_public_test": "" if hidden else func,
        "public_test_source": "" if hidden else test_src[:2000],
        "names_in_first_public_test_not_in_required_api": extra,
        "error": excerpt,
        "isolation": isolation,
        "submission_files": submission_tree(run_dir),
        "impl_snippets": snippet_for_symbol(run_dir, symbols),
        "events": parse_events(run_dir / "agent" / "openhands_events.jsonl"),
        "evidence_log": str((run_dir / log_name).relative_to(ROOT)) if (run_dir / log_name).exists() else "",
    }


def main() -> None:
    rows = list(csv.DictReader(ROWS.open(encoding="utf-8")))
    # L0: all public failures of post models
    public_fails = [
        r
        for r in rows
        if r["model"] in POST_MODELS
        and r["artifact_fail"] == "True"
        and r["first_failure_stage"] == "public_failure"
    ]
    l0 = []
    for row in public_fails:
        pkt = packet_for(row)
        l0.append(
            {
                "model": row["model"],
                "task_id": row["task_id"],
                "first_public_test": pkt["first_public_test"],
                "error_types": pkt["error"]["error_types"],
                "extra_names": pkt["names_in_first_public_test_not_in_required_api"],
                "known_public_defect_task": pkt["known_public_defect_task"],
                "excerpt": pkt["error"]["excerpt"][:400],
            }
        )
    (OUT / "l0_postsample_public_screen.json").write_text(
        json.dumps({"n": len(l0), "rows": l0}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    sample = sample_rows(rows)
    packets = [packet_for(r) for r in sample]
    (OUT / "postsample_l1_packets.json").write_text(
        json.dumps(
            {
                "seed": SAMPLE_SEED,
                "n": len(packets),
                "by_model": dict(Counter(p["model"] for p in packets)),
                "packets": packets,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    # process tags: Pro+Flash valid artifact fails + postsample
    pf = [
        r
        for r in rows
        if r["model"] in {"deepseek-v4-pro", "deepseek-v4-flash"}
        and r["artifact_fail"] == "True"
    ]
    proc_rows = []
    seen = set()
    for row in pf + sample:
        key = (row["model"], row["task_id"])
        if key in seen:
            continue
        seen.add(key)
        run_dir = SUITES[row["model"]] / row["task_id"]
        ev = parse_events(run_dir / "agent" / "openhands_events.jsonl")
        proc_rows.append(
            {
                "model": row["model"],
                "task_id": row["task_id"],
                "first_failure_stage": row["first_failure_stage"],
                "in_pro_flash_census": row["model"] in {"deepseek-v4-pro", "deepseek-v4-flash"},
                **ev,
            }
        )
    (OUT / "process_tag_screen.json").write_text(
        json.dumps(
            {
                "n": len(proc_rows),
                "tag_counts": dict(Counter(r["process_tag"] for r in proc_rows)),
                "pro_flash_tags": dict(
                    Counter(r["process_tag"] for r in proc_rows if r["in_pro_flash_census"])
                ),
                "rows": proc_rows,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "l0_public": len(l0),
                "sample": len(packets),
                "process": len(proc_rows),
                "process_tags": dict(Counter(r["process_tag"] for r in proc_rows)),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
