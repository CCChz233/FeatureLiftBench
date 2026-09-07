#!/usr/bin/env python3
"""Build desensitized evidence packets for Pro+Flash artifact-level failures."""
from __future__ import annotations

import ast
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
TAXONOMY = ROOT / "artifacts/research_analysis/python200_hard_task_taxonomy.csv"
TASKS = ROOT / "benchmark/python200_hard_tasks"
ROWS = OUT / "task_results.csv"

SUITES = {
    "deepseek-v4-pro": ROOT / "experiments/python/openhands/deepseek-v4-pro/python150-prime-v2-main-r1",
    "deepseek-v4-flash": ROOT / "experiments/python/openhands/deepseek-v4-flash/python200-prime-v2-main-r1",
}

FAIL_RES = [
    re.compile(r"FAILED .*::(\S+)"),
    re.compile(r"(AttributeError|ImportError|ModuleNotFoundError|TypeError|ValueError|KeyError|AssertionError|NameError): (.+)"),
    re.compile(r"E\s+(AttributeError|ImportError|ModuleNotFoundError|TypeError|ValueError|KeyError|AssertionError|NameError): (.+)"),
]


def defined_names(submission: Path) -> set[str]:
    names: set[str] = set()
    root = submission / "featurelifted"
    if not root.exists():
        root = submission
    for py in root.rglob("*.py"):
        if py.name.startswith("test"):
            continue
        try:
            tree = ast.parse(py.read_text(encoding="utf-8", errors="replace"), filename=str(py))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
                names.add(node.name)
            elif isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        names.add(t.id)
        try:
            rel = str(py.relative_to(root).with_suffix("")).replace("/", ".")
            names.add(rel)
        except ValueError:
            pass
    return names


def required_paths(meta: dict) -> list[str]:
    api = ((meta.get("public_spec") or {}).get("required_api") or [])
    out = []
    for item in api:
        if isinstance(item, dict) and item.get("path"):
            out.append(str(item["path"]))
            for member in item.get("members") or []:
                if isinstance(member, dict) and member.get("path"):
                    out.append(str(member["path"]))
        elif isinstance(item, str):
            out.append(item)
    return out


def leaf(path: str) -> str:
    return path.rsplit(".", 1)[-1]


def log_excerpt(task_dir: Path, stage: str) -> dict:
    name = {
        "public_failure": "public.stdout",
        "hidden_failure": "hidden.stdout",
        "build_failure": "build.stdout",
        "isolation_failure": "isolation.stdout",
    }.get(stage, "public.stdout")
    path = task_dir / "eval" / "logs" / name
    alt = task_dir / "eval" / "logs" / name.replace(".stdout", ".stderr")
    text = ""
    for p in (path, alt):
        if p.is_file():
            text += p.read_text(encoding="utf-8", errors="replace")
    # Prefer short-test summary / error lines; drop hidden test names from stored packet
    errors = []
    for rx in FAIL_RES:
        for m in rx.finditer(text):
            errors.append(" | ".join(g for g in m.groups() if g))
    kinds = sorted({e.split(":")[0].split("|")[0].strip() for e in errors if e})
    # keep last 8 interesting lines without nodeids
    interesting = []
    for line in text.splitlines():
        if any(k in line for k in ("Error", "FAILED", "E   ", "assert ", "ImportError", "AttributeError")):
            cleaned = re.sub(r"[\w./-]+::[\w\[\],-]+", "<test>", line)
            cleaned = re.sub(r"hidden_tests/\S+", "<hidden>", cleaned)
            interesting.append(cleaned.strip()[:220])
    return {
        "error_kinds": kinds[:8],
        "error_hits": errors[:8],
        "lines": interesting[-12:],
    }


def trajectory_stats(task_dir: Path) -> dict:
    ev = task_dir / "agent" / "openhands_events.jsonl"
    reads = edits = 0
    repo_reads = 0
    if not ev.is_file():
        return {"events": 0, "reads": 0, "edits": 0, "repo_reads": 0}
    n = 0
    for line in ev.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        n += 1
        try:
            o = json.loads(line)
        except json.JSONDecodeError:
            continue
        action = o.get("action") if isinstance(o.get("action"), dict) else {}
        cmd = str(action.get("command") or o.get("tool_name") or "")
        path = str(action.get("path") or "")
        low = (cmd + " " + path).lower()
        if "view" in low or "read" in low or cmd in {"view", "read"}:
            reads += 1
            if "/repo" in path or path.endswith("/repo") or "/flb/workspace/repo" in path:
                repo_reads += 1
        if cmd in {"create", "str_replace", "insert", "edit"} or "str_replace" in low:
            edits += 1
    return {"events": n, "reads": reads, "edits": edits, "repo_reads": repo_reads}


def isolation_bits(result: dict) -> dict:
    iso = result.get("isolation") or {}
    return {
        "forbidden_imports_pass": iso.get("forbidden_imports_pass"),
        "forbidden_dependencies_pass": iso.get("forbidden_dependencies_pass"),
        "runtime_import_origin_pass": iso.get("runtime_import_origin_pass"),
        "path_leakage": (result.get("compactness") or {}).get("path_leakage"),
        "forbidden_source_import": (result.get("compactness") or {}).get("forbidden_source_import"),
    }


def clause_ids(task_id: str, stage: str, log_text_hits: list[str]) -> list[str]:
    contract_path = TASKS / task_id / "evaluation" / "behavior_contract.json"
    if not contract_path.is_file():
        return []
    d = json.loads(contract_path.read_text(encoding="utf-8"))
    key = "public_test_mappings" if stage == "public_failure" else "hidden_test_mappings"
    mappings = d.get(key) or []
    ids: list[str] = []
    for item in mappings:
        if not isinstance(item, dict):
            continue
        nodeid = str(item.get("nodeid") or "")
        # If we can match a failed test leaf from hits, keep those clauses; else keep all mapped for the stage (too broad). Skip all-dump.
        leaves = [h.split("|")[0].strip() for h in log_text_hits]
        if any(leaf and leaf in nodeid for leaf in leaves):
            ids.extend(item.get("public_clause_ids") or item.get("clause_ids") or [])
    return sorted(set(ids))[:8]


def main() -> None:
    tax = {}
    with TAXONOMY.open() as handle:
        for row in csv.DictReader(handle):
            tax[row["task_id"]] = row
    packets = []
    with ROWS.open() as handle:
        for row in csv.DictReader(handle):
            if row["model"] not in SUITES:
                continue
            if row["artifact_fail"] != "True":
                continue
            if row["functional_pass"] == "True":
                continue
            tid = row["task_id"]
            suite = SUITES[row["model"]]
            task_dir = suite / tid
            meta_path = TASKS / tid / "metadata.json"
            meta = json.loads(meta_path.read_text()) if meta_path.is_file() else {}
            required = required_paths(meta)
            names = defined_names(task_dir / "submission")
            missing = [p for p in required if leaf(p) not in names]
            present = [p for p in required if leaf(p) in names]
            result_path = task_dir / "eval" / "result.json"
            result = json.loads(result_path.read_text()) if result_path.is_file() else {}
            stage = row["first_failure_stage"]
            excerpt = log_excerpt(task_dir, stage)
            n_files = int(row.get("submission_file_count") or 0)
            packets.append(
                {
                    "model": row["model"],
                    "task_id": tid,
                    "lift_type": row.get("lift_type"),
                    "hard3": row.get("hard3") == "True",
                    "feature_family": tax.get(tid, {}).get("feature_family_v2"),
                    "first_failure_stage": stage,
                    "n_files": n_files,
                    "submitted_loc": row.get("submitted_loc"),
                    "required_api_n": len(required),
                    "required_present_n": len(present),
                    "required_missing_leaves": sorted({leaf(p) for p in missing})[:20],
                    "log": excerpt,
                    "clause_ids": clause_ids(tid, stage, excerpt.get("error_hits") or []),
                    "trajectory": trajectory_stats(task_dir),
                    "isolation": isolation_bits(result) if stage == "isolation_failure" else {},
                }
            )
    (OUT / "f3_evidence_packets.json").write_text(json.dumps(packets, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"n": len(packets), "by_model": {m: sum(1 for p in packets if p["model"]==m) for m in SUITES}, "by_stage": {}}, indent=2))
    from collections import Counter
    print("stage", Counter((p["model"], p["first_failure_stage"]) for p in packets))


if __name__ == "__main__":
    main()
