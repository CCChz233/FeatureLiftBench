#!/usr/bin/env python3
"""Build an auditable failure-attribution dataset for the frozen 550-run corpus.

The script deliberately separates direct evaluator observations, conservative
trajectory-derived indicators, and low-confidence causal interpretations.  It
does not read hidden-test source when deriving agent-side behavior features;
hidden evaluator logs are used only after the run to identify the observed
contract failure.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = Path(__file__).resolve().parent
BASE_CSV = REPO_ROOT / "reports/token_efficiency_20260720/trajectory_records_550.csv"
TAXONOMY_CSV = REPO_ROOT / "artifacts/research_analysis/python150_task_taxonomy.csv"

SOURCE_SUFFIXES = {".py", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".txt"}
NON_CODE_ORACLE_NAMES = {"LICENSE", "LICENSE.txt", "pyproject.toml", "setup.py", "setup.cfg"}
READ_VERBS = re.compile(r"\b(?:cat|sed|head|tail|less|more|rg|grep|awk|find|view)\b", re.I)
WRITE_VERBS = re.compile(r"(?:\bcp\b|\bmv\b|\btee\b|\bmkdir\b|>|apply_patch|touch)", re.I)
TEST_RE = re.compile(r"\b(?:pytest|unittest|python\s+-m\s+pytest)\b", re.I)
PYTHON_RE = re.compile(r"\b(?:python|python3|uv\s+run\s+python)\b", re.I)
PUBLIC_RE = re.compile(r"public_tests?", re.I)
INSTALL_RE = re.compile(r"(?:pip|uv)\s+(?:install|sync)|python\s+-m\s+build", re.I)
FORBIDDEN_CHECK_RE = re.compile(r"forbidden|grep.+import|audit_output_imports|original_import", re.I | re.S)
PACKAGE_CHECK_RE = re.compile(r"submission/featurelifted|import\s+featurelifted|from\s+featurelifted", re.I)

DYNAMIC_PATTERNS: dict[str, re.Pattern[str]] = {
    "parser_state": re.compile(r"parser state|stateful|across calls?|previous call|history|token stream", re.I),
    "framework_lifecycle": re.compile(r"framework|lifecycle|hook|callback|decorator|fixture|setup", re.I),
    "config_environment": re.compile(r"environment variable|os\.environ|env var|cwd|working directory|config", re.I),
    "resource_packaging": re.compile(r"package resource|importlib\.resources|resource lookup|resource file|wheel|package data", re.I),
    "dynamic_import_plugin": re.compile(r"dynamic import|entry point|plugin|discovery|importlib|lazy import", re.I),
    "global_state_registry": re.compile(r"global state|module-level|registry|singleton|monkey.?patch|cache state", re.I),
    "reflection_dispatch": re.compile(r"getattr|setattr|reflection|dynamic dispatch|__getattr__|metaclass", re.I),
    "third_party_contract": re.compile(r"third.party|runtime coercion|preparedrequest|dependency version", re.I),
}

DYNAMIC_FAILURE_PATTERNS: dict[str, re.Pattern[str]] = {
    "parser_state": re.compile(r"across_calls?|second_call|repeat|history|reset|stateful|stream|incremental", re.I),
    "framework_lifecycle": re.compile(r"callback|hook|decorator|plugin|extension|fixture|setup|teardown|inherit|lifecycle|commit|conflict", re.I),
    "config_environment": re.compile(r"env|xdg|cwd|working_dir|path|config|profile|precedence", re.I),
    "resource_packaging": re.compile(r"resource|package_data|wheel|record_path|traversable|read_(?:text|binary)", re.I),
    "dynamic_import_plugin": re.compile(r"entry_point|plugin|extension|discover|lazy|dynamic_import|module_load", re.I),
    "global_state_registry": re.compile(r"global|registry|cache|reset|history|call_count|second_call|commit|conflict|signal", re.I),
    "reflection_dispatch": re.compile(r"getattr|attribute|dispatch|metaclass|class_construction", re.I),
    "third_party_contract": re.compile(r"preparedrequest|request|response|dependency|coercion|adapter", re.I),
}


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (json.JSONDecodeError, OSError):
        return {}
    return payload if isinstance(payload, dict) else {}


def boolish(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    text = str(value).strip().lower()
    if text == "true":
        return True
    if text == "false":
        return False
    return None


def text_content(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(text_content(item) for item in value)
    if isinstance(value, dict):
        if isinstance(value.get("text"), str):
            return value["text"]
        return "\n".join(text_content(v) for v in value.values())
    return ""


def event_agent_text(event: dict[str, Any]) -> str:
    if event.get("source") != "agent":
        return ""
    parts = [text_content(event.get(k)) for k in ("reasoning_content", "thought", "message")]
    action = event.get("action")
    if isinstance(action, dict):
        parts.extend(text_content(action.get(k)) for k in ("description", "summary", "prompt", "task_list"))
    return "\n".join(p for p in parts if p)


def action_text(event: dict[str, Any]) -> str:
    action = event.get("action")
    if not isinstance(action, dict):
        return ""
    return "\n".join(
        text_content(action.get(k))
        for k in ("command", "path", "description", "summary", "prompt", "file_text", "new_str")
        if action.get(k) is not None
    )


def observation_text(event: dict[str, Any]) -> str:
    obs = event.get("observation")
    return text_content(obs) if isinstance(obs, dict) else ""


def read_events(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    if not path.is_file():
        return events
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(item, dict):
                events.append(item)
    return events


def locate_task_dir(task_id: str) -> Path:
    for base in ("benchmark/tasks", "benchmark/batch3_pilot", "benchmark/staging", "benchmark/sanity"):
        path = REPO_ROOT / base / task_id
        if (path / "metadata.json").is_file():
            return path
    raise FileNotFoundError(task_id)


def normalize_expected_path(raw: str) -> str:
    path = raw.replace("\\", "/").lstrip("./")
    if "/repo/" in path:
        path = path.split("/repo/", 1)[1]
    if path.startswith("repo/"):
        path = path[5:]
    return path


def entry_files(task_dir: Path, metadata: dict[str, Any]) -> list[str]:
    repo = task_dir / "repo"
    candidates: list[str] = []
    feature = metadata.get("feature") if isinstance(metadata.get("feature"), dict) else {}
    for entry in feature.get("source_entrypoints") or []:
        parts = str(entry).split(".")
        for end in range(len(parts), 0, -1):
            stem = "/".join(parts[:end])
            for rel in (f"{stem}.py", f"{stem}/__init__.py", f"src/{stem}.py", f"src/{stem}/__init__.py"):
                if (repo / rel).is_file():
                    candidates.append(rel)
                    break
            else:
                continue
            break
    return list(dict.fromkeys(candidates))


def oracle_files(task_dir: Path) -> list[str]:
    oracle = load_json(task_dir / "evaluation/oracle_manifest.json")
    values = oracle.get("required_source_files") or []
    return list(dict.fromkeys(normalize_expected_path(str(v)) for v in values if str(v).strip()))


def source_repo_metrics(task_dir: Path) -> tuple[int, int]:
    files = [p for p in (task_dir / "repo").rglob("*") if p.is_file() and p.suffix in SOURCE_SUFFIXES]
    loc = 0
    for path in files:
        try:
            loc += len(path.read_text(encoding="utf-8", errors="replace").splitlines())
        except OSError:
            pass
    return len(files), loc


def mechanism_set(tax: pd.Series) -> set[str]:
    normalized = str(tax.get("normalized_entanglement_types") or "")
    mechanisms = {m for m in DYNAMIC_PATTERNS if m in normalized}
    if boolish(tax.get("has_dynamic_import")):
        mechanisms.add("dynamic_import_plugin")
    if boolish(tax.get("has_global_state")) or boolish(tax.get("has_registry")):
        mechanisms.add("global_state_registry")
    if boolish(tax.get("has_framework_lifecycle")):
        mechanisms.add("framework_lifecycle")
    return mechanisms


def primary_dynamic_task(tax: pd.Series) -> bool:
    """Narrow, outcome-blind dynamic-runtime definition.

    Local parser/data-structure state alone is excluded.  Included mechanisms
    cross a call/module/process boundary or depend on import, lifecycle,
    environment, resource, global, or session state.
    """
    state = str(tax.get("feature_statefulness") or "")
    normalized = str(tax.get("normalized_entanglement_types") or "")
    explicit = any(
        boolish(tax.get(c))
        for c in ("has_dynamic_import", "has_global_state", "has_framework_lifecycle")
    )
    annotated = any(
        term in normalized
        for term in ("config_environment", "resource_packaging", "dynamic_import_plugin", "global_state_registry", "framework_lifecycle")
    )
    return bool(explicit or annotated or state in {"session_state", "global_state", "lifecycle_state"})


def broad_dynamic_task(tax: pd.Series) -> bool:
    # Retain the pre-existing metadata heuristic as a sensitivity definition.
    # It is independent of the run outcome and is narrower than treating every
    # parser/local-state task as a dynamic-runtime dependency task.
    return boolish(tax.get("dynamic_state_task")) is True


def expected_path_in_text(expected: str, text: str) -> bool:
    expected = expected.replace("\\", "/")
    normalized = text.replace("\\", "/")
    return expected in normalized or f"repo/{expected}" in normalized


def parse_trajectory(
    events: list[dict[str, Any]], expected_entries: list[str], closure_files: list[str], mechanisms: set[str]
) -> dict[str, Any]:
    read_files: set[str] = set()
    explicit_reads: defaultdict[str, list[str]] = defaultdict(list)
    source_view_counts: Counter[str] = Counter()
    source_repeat_ids: list[str] = []
    terminal_commands: list[tuple[int, str, str]] = []
    edit_indices: list[int] = []
    public_test_indices: list[int] = []
    verification_indices: list[int] = []
    runtime_probe_indices: list[int] = []
    dynamic_probe_indices: list[int] = []
    recognition_indices: list[int] = []
    recognition_ids: list[str] = []
    condensation_indices: list[int] = []
    condensation_ids: list[str] = []
    forgotten_count = 0
    summary_retains_dynamic = False
    symbol_text_parts: list[str] = []

    for idx, event in enumerate(events):
        event_id = str(event.get("id") or "")
        kind = str(event.get("kind") or "")
        agent_text = event_agent_text(event)
        act_text = action_text(event)
        obs_text = observation_text(event)
        action = event.get("action") if isinstance(event.get("action"), dict) else {}
        action_kind = str(action.get("kind") or "")
        command = str(action.get("command") or "")
        combined_tool = f"{act_text}\n{obs_text}"
        symbol_text_parts.append(f"{agent_text}\n{combined_tool}")

        if kind == "Condensation":
            condensation_indices.append(idx)
            condensation_ids.append(event_id)
            forgotten_count += len(event.get("forgotten_event_ids") or [])
            summary = str(event.get("summary") or "")
            if any(DYNAMIC_PATTERNS[m].search(summary) for m in mechanisms if m in DYNAMIC_PATTERNS):
                summary_retains_dynamic = True

        for expected in closure_files:
            if not expected_path_in_text(expected, combined_tool):
                continue
            # A view or read command is direct inspection evidence.  A task
            # observation containing the path is accepted as delegated read.
            direct_view = action_kind == "FileEditorAction" and action.get("command") == "view"
            terminal_read = action_kind == "TerminalAction" and READ_VERBS.search(command)
            delegated_observation = kind == "ObservationEvent" and bool(obs_text)
            if direct_view or terminal_read or delegated_observation:
                read_files.add(expected)
                explicit_reads[expected].append(event_id)

        if action_kind == "FileEditorAction":
            path = str(action.get("path") or "").replace("\\", "/")
            if action.get("command") == "view" and "/repo/" in path:
                rel = path.split("/repo/", 1)[1]
                source_view_counts[rel] += 1
                if source_view_counts[rel] > 1:
                    source_repeat_ids.append(event_id)
            if action.get("command") in {"create", "str_replace", "insert"} and (
                "/submission/" in path or path.startswith("submission/")
            ):
                edit_indices.append(idx)

        if action_kind == "TerminalAction" and command:
            terminal_commands.append((idx, command, event_id))
            if ("submission/" in command or "/submission" in command) and WRITE_VERBS.search(command):
                edit_indices.append(idx)
            if TEST_RE.search(command):
                verification_indices.append(idx)
                if PUBLIC_RE.search(command):
                    public_test_indices.append(idx)
            elif PACKAGE_CHECK_RE.search(command) or FORBIDDEN_CHECK_RE.search(command) or INSTALL_RE.search(command):
                verification_indices.append(idx)
            is_python_probe = PYTHON_RE.search(command) and not re.search(r"py_compile|compileall|\s+-m\s+build", command)
            is_targeted_test = TEST_RE.search(command) and not PUBLIC_RE.search(command)
            if is_python_probe or is_targeted_test:
                runtime_probe_indices.append(idx)
                if any(DYNAMIC_PATTERNS[m].search(command) for m in mechanisms if m in DYNAMIC_PATTERNS):
                    dynamic_probe_indices.append(idx)

        # Recognition is based on agent-authored interpretation, not source
        # output containing a keyword.
        if agent_text and any(DYNAMIC_PATTERNS[m].search(agent_text) for m in mechanisms if m in DYNAMIC_PATTERNS):
            recognition_indices.append(idx)
            recognition_ids.append(event_id)

    symbols_blob = "\n".join(symbol_text_parts)
    entry_read = [p for p in expected_entries if p in read_files]
    closure_code = [p for p in closure_files if Path(p).name not in NON_CODE_ORACLE_NAMES and Path(p).suffix in SOURCE_SUFFIXES]
    if not closure_code:
        closure_code = expected_entries
    dep_files = [p for p in closure_code if p not in expected_entries]
    dep_read = [p for p in dep_files if p in read_files]
    dep_coverage = len(dep_read) / len(dep_files) if dep_files else (1.0 if entry_read else 0.0)
    if dep_coverage >= 0.75:
        dependency_status = "yes"
    elif dep_coverage < 0.5:
        dependency_status = "no"
    else:
        dependency_status = "unclear"

    last_edit = max(edit_indices) if edit_indices else None
    post_edit_verification = bool(last_edit is not None and any(i > last_edit for i in verification_indices))
    post_edit_public = bool(last_edit is not None and any(i > last_edit for i in public_test_indices))
    exact_repeat_commands = sum(v - 1 for v in Counter(" ".join(c.split()) for _, c, _ in terminal_commands).values() if v > 1)
    dynamic_recognized = bool(recognition_indices)
    before_condensation = bool(
        recognition_indices and condensation_indices and min(recognition_indices) < max(condensation_indices)
    )
    after_last_condensation = bool(
        recognition_indices and condensation_indices and max(recognition_indices) > max(condensation_indices)
    )
    memory_loss_candidate = bool(before_condensation and not after_last_condensation and not summary_retains_dynamic)

    return {
        "correct_entry_file": bool(entry_read),
        "entry_files_expected": json.dumps(expected_entries, ensure_ascii=False),
        "entry_files_read": json.dumps(entry_read, ensure_ascii=False),
        "entry_file_evidence_ids": json.dumps([explicit_reads[p][0] for p in entry_read if explicit_reads[p]], ensure_ascii=False),
        "all_tool_text": symbols_blob,
        "closure_code_file_count": len(closure_code),
        "closure_files_read_count": sum(p in read_files for p in closure_code),
        "dependency_file_count": len(dep_files),
        "dependency_files_read_count": len(dep_read),
        "dependency_read_coverage": dep_coverage,
        "key_direct_dependencies_identified": dependency_status,
        "runtime_probe_count": len(runtime_probe_indices),
        "dynamic_runtime_probe_count": len(dynamic_probe_indices),
        "dynamic_dependency_recognized": dynamic_recognized,
        "dynamic_recognition_evidence_ids": json.dumps(recognition_ids[:5], ensure_ascii=False),
        "last_edit_index": last_edit,
        "fresh_final_verification": post_edit_verification,
        "fresh_public_verification": post_edit_public,
        "unchanged_repeated_reads": sum(v - 1 for v in source_view_counts.values() if v > 1),
        "unchanged_repeated_read_evidence_ids": json.dumps(source_repeat_ids[:8], ensure_ascii=False),
        "exact_repeated_terminal_commands": exact_repeat_commands,
        "condensation_events": len(condensation_indices),
        "forgotten_event_count": forgotten_count,
        "dynamic_recognized_before_condensation": before_condensation,
        "dynamic_recognized_after_last_condensation": after_last_condensation,
        "condensation_summary_retained_dynamic": summary_retains_dynamic,
        "memory_loss_candidate": memory_loss_candidate,
    }


def target_symbols(metadata: dict[str, Any], task_dir: Path) -> list[str]:
    oracle = load_json(task_dir / "evaluation/oracle_manifest.json")
    values = oracle.get("target_symbols") or oracle.get("target_api") or []
    if not values:
        feature = metadata.get("feature") if isinstance(metadata.get("feature"), dict) else {}
        values = feature.get("source_entrypoints") or []
    symbols = [str(v).split(".")[-1] for v in values]
    return [s for s in dict.fromkeys(symbols) if s and s not in {"featurelifted", "__init__"}]


def evaluator_features(row: pd.Series) -> dict[str, Any]:
    eval_path = REPO_ROOT / str(row.get("evaluation_path") or "")
    result = load_json(eval_path)
    logs_dir = eval_path.parent / "logs"
    logs: dict[str, str] = {}
    for phase in ("build", "public", "hidden", "submission_install", "dependency_install"):
        chunks: list[str] = []
        for suffix in ("stdout", "stderr"):
            path = logs_dir / f"{phase}.{suffix}"
            if path.is_file():
                chunks.append(path.read_text(encoding="utf-8", errors="replace"))
        logs[phase] = "\n".join(chunks)
    hidden = logs.get("hidden", "")
    public = logs.get("public", "")
    failure_lines = []
    for line in (hidden or public or logs.get("build", "")).splitlines():
        s = line.strip()
        if re.search(r"(?:FAILED|ERROR|E\s+|ImportError|ModuleNotFoundError|AssertionError|SyntaxError)", s):
            failure_lines.append(s)
    hidden_nodeids = re.findall(r"(?:FAILED\s+)?(?:[^\s]*hidden_tests/)?([^\s:]+\.py::[^\s]+)", hidden)
    submission_install = result.get("submission_install") if isinstance(result.get("submission_install"), dict) else {}
    if submission_install:
        if submission_install.get("skipped"):
            clean_install = "not_tested_path_import"
        elif submission_install.get("passed") is True:
            clean_install = "passed"
        elif submission_install.get("passed") is False:
            clean_install = "failed"
        else:
            clean_install = "unknown"
    else:
        clean_install = "unknown"
    original_import = result.get("original_import_pass")
    independent = original_import is True
    if not result:
        independent = None
    return {
        "clean_install_status": clean_install,
        "original_repository_independence": independent,
        "still_depends_on_original_repo": (original_import is False) if isinstance(original_import, bool) else None,
        "hidden_failure_excerpt": " | ".join(failure_lines[:4])[:1000],
        "hidden_failure_nodeids": json.dumps(list(dict.fromkeys(hidden_nodeids))[:12], ensure_ascii=False),
        "hidden_failure_text": hidden,
        "public_failure_text": public,
        "submission_install_executed": bool(submission_install and not submission_install.get("skipped")),
    }


def boundary_status(row: pd.Series) -> str:
    if row.get("still_depends_on_original_repo") is True:
        return "no"
    ratio = row.get("extraction_ratio")
    if pd.notna(ratio) and (float(ratio) > 1.0 or float(ratio) < 0.02):
        return "unclear"
    if row.get("dependency_read_coverage", 0) >= 0.75 and boolish(row.get("submission_present")) is True:
        return "yes"
    return "unclear"


def classify_failure_stage(row: pd.Series) -> tuple[str, str, str, str]:
    if bool(row.get("formal_pass")):
        return "passed", "none", "none", "direct"
    if int(row.get("evaluator_environment_error_count") or 0) > 0:
        return "evaluator_or_environment", "H8", "none", "high"
    stop = str(row.get("stop_reason") or "")
    if stop in {"step_limit_exceeded", "timeout"} and boolish(row.get("public_pass")) is not True:
        return "budget_exhaustion", "H7", "exploration_policy_or_budget", "medium"
    if not bool(row.get("correct_entry_file")) and boolish(row.get("public_pass")) is not True:
        return "localization", "H1", "none", "weak"
    if not bool(row.get("correct_symbol")) and boolish(row.get("public_pass")) is not True:
        return "localization", "H1", "symbol_not_confirmed", "weak"
    primary = str(row.get("primary_failure") or "")
    hidden_text = str(row.get("hidden_failure_text") or "")
    public_text = str(row.get("public_failure_text") or "")
    interface_failure = bool(re.search(r"ImportError|ModuleNotFoundError|cannot import name|has no attribute", hidden_text + public_text, re.I))
    isolation_failure = bool(
        row.get("still_depends_on_original_repo") is True
        or primary == "isolation_or_forbidden_import_failure"
        or re.search(r"forbidden import|original repository", hidden_text + public_text, re.I)
    )
    if isolation_failure:
        return "boundary_recovery", "H4", "verification", "high"
    if interface_failure or primary == "dependency_closure_omission":
        return "dependency_discovery", "H2", "verification", "high"
    if (
        boolish(row.get("public_pass")) is True
        and boolish(row.get("hidden_pass")) is False
        and bool(row.get("dynamic_runtime_task"))
        and bool(row.get("dynamic_failure_evidence"))
    ):
        if not bool(row.get("dynamic_dependency_recognized")) and int(row.get("dynamic_runtime_probe_count") or 0) == 0:
            return "dynamic_semantics", "H3", "exploration_policy", "medium"
        if bool(row.get("memory_loss_candidate")):
            return "dynamic_semantics", "H3", "memory_state_management", "weak"
        return "dynamic_semantics", "H3", "capability_or_implementation", "medium"
    if primary in {"packaging_or_build_failure", "build_syntax_or_version_failure"}:
        if not bool(row.get("fresh_final_verification")):
            return "verification", "H6", "implementation", "high"
        return "implementation", "H5", "verification", "high"
    if boolish(row.get("public_pass")) is False:
        if not bool(row.get("fresh_final_verification")) or not bool(row.get("public_executed")):
            return "verification", "H6", "implementation", "medium"
        return "implementation", "H5", "none", "medium"
    if boolish(row.get("public_pass")) is True and boolish(row.get("hidden_pass")) is False:
        return "implementation", "H5", "verification", "medium"
    if stop in {"step_limit_exceeded", "timeout"}:
        return "budget_exhaustion", "H7", "none", "medium"
    if primary == "missing_submission":
        return "budget_exhaustion", "H7", "workflow_failure", "medium"
    return "unclear", "unclear", "none", "weak"


def wilson(success: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (math.nan, math.nan)
    p = success / n
    den = 1 + z * z / n
    center = (p + z * z / (2 * n)) / den
    half = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / den
    return center - half, center + half


def rate_row(group: pd.DataFrame, label: str) -> dict[str, Any]:
    formal = group["formal_pass"].astype(bool)
    hidden_observed = group["hidden_pass"].notna()
    public_pass = group["public_pass"].eq(True)
    phhf = public_pass & group["hidden_pass"].eq(False)
    lo, hi = wilson(int(formal.sum()), len(group))
    return {
        "group": label,
        "runs": len(group),
        "tasks": group["task_id"].nunique(),
        "formal_passes": int(formal.sum()),
        "pass_rate": formal.mean(),
        "pass_ci_low": lo,
        "pass_ci_high": hi,
        "public_pass_hidden_fail": int(phhf.sum()),
        "hidden_failure_rate_given_public": phhf.sum() / public_pass.sum() if public_pass.sum() else math.nan,
        "hidden_pass_rate_observed": group.loc[hidden_observed, "hidden_pass"].eq(True).mean() if hidden_observed.any() else math.nan,
        "median_tokens": group["total_tokens"].median(),
        "median_repeated_reads": group["unchanged_repeated_reads"].median(),
        "repeat_read_affected_rate": group["unchanged_repeated_reads"].gt(0).mean(),
        "runtime_probe_rate": group["runtime_probe_count"].gt(0).mean(),
        "dynamic_probe_rate": group["dynamic_runtime_probe_count"].gt(0).mean(),
        "dynamic_recognition_rate": group["dynamic_dependency_recognized"].mean(),
        "fresh_final_verification_rate": group["fresh_final_verification"].mean(),
        "condensation_rate": group["condensation_events"].gt(0).mean(),
    }


def regression(df: pd.DataFrame) -> pd.DataFrame:
    import statsmodels.formula.api as smf

    work = df.copy()
    work["log_repo_loc"] = np.log1p(work["repo_loc"])
    work["log_reference_loc"] = np.log1p(work["reference_loc"].fillna(work["reference_loc"].median()))
    work["formal_pass_int"] = work["formal_pass"].astype(int)
    work["condensation_any"] = work["condensation_events"].gt(0).astype(int)
    work["repeat_any"] = work["unchanged_repeated_reads"].gt(0).astype(int)
    work["dynamic_int"] = work["dynamic_runtime_task"].astype(int)
    work["legacy_dynamic_int"] = work["broad_dynamic_task"].astype(int)
    formulas = {
        "primary_preoutcome": "formal_pass_int ~ dynamic_int + C(model) + C(split) + log_repo_loc + log_reference_loc + public_test_count + entanglement_count",
        "primary_split_interaction": "formal_pass_int ~ dynamic_int * C(split) + C(model) + log_repo_loc + log_reference_loc + public_test_count + entanglement_count",
        "primary_plus_trajectory": "formal_pass_int ~ dynamic_int + C(model) + C(split) + log_repo_loc + log_reference_loc + public_test_count + entanglement_count + condensation_any + repeat_any",
        "legacy_definition_sensitivity": "formal_pass_int ~ legacy_dynamic_int + C(model) + C(split) + log_repo_loc + log_reference_loc + public_test_count + entanglement_count",
    }
    rows: list[dict[str, Any]] = []
    for name, formula in formulas.items():
        try:
            fit = smf.logit(formula, data=work).fit(disp=False, cov_type="cluster", cov_kwds={"groups": work["task_id"]})
        except Exception as exc:
            rows.append({"specification": name, "term": "ERROR", "error": str(exc)})
            continue
        for term, coef in fit.params.items():
            if term not in {"dynamic_int", "dynamic_int:C(split)[T.hard50]", "legacy_dynamic_int", "condensation_any", "repeat_any"}:
                continue
            se = fit.bse[term]
            rows.append(
                {
                    "specification": name,
                    "term": term,
                    "odds_ratio": math.exp(coef),
                    "ci_low": math.exp(coef - 1.96 * se),
                    "ci_high": math.exp(coef + 1.96 * se),
                    "p_value": fit.pvalues[term],
                    "n": int(fit.nobs),
                    "clusters": work["task_id"].nunique(),
                    "pseudo_r2": fit.prsquared,
                }
            )
    return pd.DataFrame(rows)


def select_cases(df: pd.DataFrame, n: int = 16) -> pd.DataFrame:
    candidates = df[df["correct_entry_file"] & df["submission_present"] & ~df["formal_pass"]].copy()
    candidates["case_priority"] = (
        candidates["public_pass"].eq(True).astype(int) * 8
        + candidates["hidden_pass"].eq(False).astype(int) * 5
        + candidates["dynamic_runtime_task"].astype(int) * 3
        + candidates["hidden_failure_excerpt"].ne("").astype(int) * 2
        + candidates["fresh_final_verification"].astype(int)
    )
    selected: list[int] = []
    quotas = {
        "dynamic_semantics": 4,
        "dependency_discovery": 4,
        "implementation": 3,
        "boundary_recovery": 2,
        "budget_exhaustion": 2,
        "verification": 1,
    }
    for stage, quota in quotas.items():
        pool = candidates[candidates["earliest_failure_stage"].eq(stage)].sort_values(
            ["case_priority", "total_tokens"], ascending=[False, False]
        )
        if stage == "dynamic_semantics":
            for _, group in pool.groupby("failure_subtype"):
                selected.append(group.index[0])
        for idx in pool.index:
            if sum(candidates.loc[i, "earliest_failure_stage"] == stage for i in dict.fromkeys(selected)) >= quota:
                break
            selected.append(idx)
    # Ensure every model is present, then fill by evidentiary priority.
    for _, group in candidates.sort_values("case_priority", ascending=False).groupby("model"):
        selected.append(group.index[0])
    for idx in candidates.sort_values(["case_priority", "total_tokens"], ascending=[False, False]).index:
        selected.append(idx)
    selected = list(dict.fromkeys(selected))[:n]
    out = candidates.loc[selected].copy()
    keep = [
        "task_id", "model", "split", "dynamic_runtime_task", "dynamic_mechanisms", "dynamic_failure_mechanisms",
        "entanglement_description", "metadata_signals", "correct_entry_file", "correct_symbol",
        "dependency_read_coverage", "runtime_probe_count", "dynamic_runtime_probe_count",
        "dynamic_dependency_recognized", "fresh_final_verification", "condensation_events",
        "memory_loss_candidate", "public_pass", "hidden_pass", "clean_install_status",
        "still_depends_on_original_repo", "earliest_failure_stage", "primary_hypothesis",
        "failure_subtype", "attribution_confidence", "hidden_failure_excerpt", "trajectory_path",
        "evaluation_path", "total_tokens",
    ]
    out = out[keep].sort_values(["earliest_failure_stage", "task_id", "model"])
    return out


def missed_behavior(row: pd.Series) -> str:
    excerpt = str(row.get("hidden_failure_excerpt") or "")
    match = re.search(r"cannot import name ['\"]([^'\"]+)", excerpt, re.I)
    if match:
        return f"missing exported API: {match.group(1)}"
    match = re.search(r"has no attribute ['\"]([^'\"]+)", excerpt, re.I)
    if match:
        return f"missing behavior/API member: {match.group(1)}"
    nodeids = str(row.get("hidden_failure_nodeids") or "")
    tests = re.findall(r"::([A-Za-z0-9_]+)", nodeids + "\n" + excerpt)
    if tests:
        return ", ".join(tests[:3]).replace("test_", "").replace("_", " ")
    if row.get("earliest_failure_stage") == "boundary_recovery":
        return "submission isolation violated (forbidden/original-package dependency)"
    if row.get("earliest_failure_stage") == "budget_exhaustion":
        return "trajectory ended before a complete, evaluable implementation"
    try:
        signals = json.loads(str(row.get("metadata_signals") or "[]"))
    except json.JSONDecodeError:
        signals = []
    if signals:
        return str(signals[0])
    return excerpt[:240] or "not recoverable from the available evaluator log"


def enrich_cases(cases: pd.DataFrame) -> pd.DataFrame:
    cases = cases.copy()
    cases["agent_knew"] = cases.apply(
        lambda r: "; ".join(
            x for x in [
                "correct entry file" if r["correct_entry_file"] else "entry file not confirmed",
                "target symbol" if r["correct_symbol"] else "target symbol not confirmed",
                "public contract passed" if boolish(r["public_pass"]) is True else "public contract not established",
                "dynamic mechanism explicitly discussed" if r["dynamic_dependency_recognized"] else "no explicit dynamic-mechanism discussion",
            ] if x
        ), axis=1
    )
    cases["agent_actual_behavior"] = cases.apply(
        lambda r: (
            f"closure-read coverage {f'{r['dependency_read_coverage']:.0%}' if pd.notna(r['dependency_read_coverage']) else 'unknown'}; "
            f"runtime probes {int(r['runtime_probe_count'])}, dynamic-targeted probes {int(r['dynamic_runtime_probe_count'])}; "
            f"fresh post-edit verification {'yes' if r['fresh_final_verification'] else 'no'}; "
            f"condensations {int(r['condensation_events'])}"
        ), axis=1
    )
    cases["missed_behavior_or_dependency"] = cases.apply(missed_behavior, axis=1)
    cases["visibility_of_missing_information"] = cases.apply(
        lambda r: (
            "runtime-coupled candidate; the exact causal mechanism still lacks runtime gold"
            if r["earliest_failure_stage"] == "dynamic_semantics"
            else "statically visible API/dependency closure"
            if r["earliest_failure_stage"] == "dependency_discovery"
            else "execution-visible behavioral mismatch"
            if r["earliest_failure_stage"] == "implementation"
            else "workflow/boundary evidence"
        ), axis=1
    )
    cases["discovery_opportunity"] = cases.apply(
        lambda r: (
            "yes—runtime probes were available but not targeted at the failing mechanism"
            if r["runtime_probe_count"] > 0 and r["dynamic_runtime_probe_count"] == 0
            else "yes—at least one targeted runtime probe was executed"
            if r["dynamic_runtime_probe_count"] > 0
            else "unclear—the trajectory did not execute a usable runtime probe"
        ), axis=1
    )
    cases["discovered_or_forgotten"] = cases.apply(
        lambda r: (
            "possible post-condensation loss; weak heuristic only"
            if r["memory_loss_candidate"]
            else "recognized and retained/used incompletely"
            if r["dynamic_dependency_recognized"]
            else "not explicitly discovered in agent-authored reasoning"
        ), axis=1
    )
    cases["most_likely_intervention"] = cases.apply(intervention, axis=1)
    return cases


def write_case_dossiers(cases: pd.DataFrame) -> None:
    lines = [
        "# Representative failure dossiers",
        "",
        "These cases were selected by a deterministic stage-diversity rule. Runtime-state labels are candidates, not adjudicated causal gold.",
        "",
    ]
    for number, (_, row) in enumerate(cases.iterrows(), 1):
        try:
            signals = json.loads(str(row.get("metadata_signals") or "[]"))
        except json.JSONDecodeError:
            signals = []
        signal_text = "; ".join(str(x) for x in signals[:3]) or str(row.get("entanglement_description") or "not annotated")
        coupling = row.get("dynamic_failure_mechanisms")
        if pd.isna(coupling) or not str(coupling).strip():
            coupling = row.get("dynamic_mechanisms")
        if pd.isna(coupling) or not str(coupling).strip():
            coupling = "no narrow dynamic mechanism matched"
        lines.extend(
            [
                f"## {number}. `{row['task_id']}` — `{row['model']}`",
                "",
                f"- **Key coupling:** {coupling}; {signal_text}",
                f"- **What the agent knew:** {row['agent_knew']}",
                f"- **Actual behavior:** {row['agent_actual_behavior']}",
                f"- **Earliest failure:** `{row['earliest_failure_stage']}` / `{row['failure_subtype']}` ({row['attribution_confidence']} confidence)",
                f"- **Missed behavior or dependency:** {row['missed_behavior_or_dependency']}",
                f"- **Visibility:** {row['visibility_of_missing_information']}",
                f"- **Could tools expose it?:** {row['discovery_opportunity']}",
                f"- **Discovery vs memory:** {row['discovered_or_forgotten']}",
                f"- **Most likely intervention:** {row['most_likely_intervention']}",
                f"- **Evidence:** `{row['trajectory_path']}`; `{row['evaluation_path']}`",
                "",
            ]
        )
    (REPORT_DIR / "representative_case_dossiers.md").write_text("\n".join(lines), encoding="utf-8")


def intervention(row: pd.Series) -> str:
    stage = row["earliest_failure_stage"]
    subtype = row["failure_subtype"]
    if stage == "dynamic_semantics":
        if subtype == "exploration_policy":
            return "targeted runtime trace/probe policy"
        if subtype == "memory_state_management":
            return "evidence-pinned memory with invalidation"
        return "runtime trace plus behavior-differential probe"
    if stage == "dependency_discovery":
        return "dependency/API closure hint and import-surface checklist"
    if stage == "boundary_recovery":
        return "forbidden-import audit plus clean isolation check"
    if stage == "verification":
        return "mandatory fresh public/install verification after final edit"
    if stage == "budget_exhaustion":
        return "phase budget with earlier stop/prune policy"
    if stage == "localization":
        return "entrypoint-to-file localization hint"
    return "targeted failing-behavior probe"


def build() -> pd.DataFrame:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    base = pd.read_csv(BASE_CSV)
    tax = pd.read_csv(TAXONOMY_CSV)
    merged = base.merge(tax, on=["task_id", "split"], how="left", validate="many_to_one")
    rows: list[dict[str, Any]] = []
    repo_metric_cache: dict[str, tuple[int, int]] = {}
    for _, raw in merged.iterrows():
        task_id = str(raw["task_id"])
        task_dir = locate_task_dir(task_id)
        metadata = load_json(task_dir / "metadata.json")
        entries = entry_files(task_dir, metadata)
        closure = list(dict.fromkeys(oracle_files(task_dir) + entries))
        mechanisms = mechanism_set(raw)
        events = read_events(REPO_ROOT / str(raw["trajectory_path"]))
        traj = parse_trajectory(events, entries, closure, mechanisms)
        direct_count = pd.to_numeric(raw.get("direct_internal_dependency_count"), errors="coerce")
        if traj["dependency_file_count"] == 0 and pd.notna(direct_count) and float(direct_count) > 0:
            traj["key_direct_dependencies_identified"] = "unclear"
            traj["dependency_read_coverage"] = math.nan
        evaluator = evaluator_features(raw)
        symbols = target_symbols(metadata, task_dir)
        tool_blob = str(traj.pop("all_tool_text"))
        correct_symbol = bool(traj["correct_entry_file"] and any(re.search(rf"\b{re.escape(s)}\b", tool_blob) for s in symbols))
        if task_id not in repo_metric_cache:
            repo_metric_cache[task_id] = source_repo_metrics(task_dir)
        repo_files, repo_loc = repo_metric_cache[task_id]
        ent = metadata.get("entanglement") if isinstance(metadata.get("entanglement"), dict) else {}
        usage = load_json((REPO_ROOT / str(raw["run_path"])).parent / "agent/usage.json")
        context = usage.get("context_audit") if isinstance(usage.get("context_audit"), dict) else {}
        out = raw.to_dict()
        out["legacy_dynamic_state_task"] = boolish(raw.get("dynamic_state_task")) is True
        out.update(traj)
        out.update(evaluator)
        out.update(
            {
                "formal_pass": str(raw.get("run_status")) == "passed",
                "correct_symbol": correct_symbol,
                "target_symbols": json.dumps(symbols, ensure_ascii=False),
                "reasonable_boundary_hypothesis": "unclear",
                "independent_implementation": evaluator["original_repository_independence"],
                "repo_file_count": repo_files,
                "repo_loc": repo_loc,
                "entanglement_count": len(str(raw.get("normalized_entanglement_types") or "").split(";")),
                "dynamic_mechanisms": ";".join(sorted(mechanisms)),
                "dynamic_mechanism_count": len(mechanisms),
                "dynamic_runtime_task": primary_dynamic_task(raw),
                "broad_dynamic_task": broad_dynamic_task(raw),
                "entanglement_description": str(ent.get("description") or ""),
                "metadata_signals": json.dumps(ent.get("signals") or [], ensure_ascii=False),
                "context_window_tokens": context.get("context_window_tokens"),
                "max_allowed_prompt_tokens": context.get("max_allowed_prompt_tokens"),
                "max_prompt_tokens_per_call": context.get("max_prompt_tokens_per_call"),
                "context_violation": context.get("context_violation"),
                "budget_or_context_truncated": str(raw.get("stop_reason")) in {"step_limit_exceeded", "timeout"} or context.get("context_violation") is True,
            }
        )
        failure_blob = f"{out.get('hidden_failure_nodeids', '')}\n{out.get('hidden_failure_excerpt', '')}"
        matched_failure_mechanisms = sorted(
            m for m in mechanisms if m in DYNAMIC_FAILURE_PATTERNS and DYNAMIC_FAILURE_PATTERNS[m].search(failure_blob)
        )
        out["dynamic_failure_evidence"] = bool(matched_failure_mechanisms)
        out["dynamic_failure_mechanisms"] = ";".join(matched_failure_mechanisms)
        out["reasonable_boundary_hypothesis"] = boundary_status(pd.Series(out))
        stage, hypothesis, subtype, confidence = classify_failure_stage(pd.Series(out))
        out.update(
            {
                "earliest_failure_stage": stage,
                "primary_hypothesis": hypothesis,
                "failure_subtype": subtype,
                "attribution_confidence": confidence,
            }
        )
        rows.append(out)
    df = pd.DataFrame(rows)
    for c in ["public_pass", "hidden_pass", "build_pass"]:
        df[c] = df[c].map(boolish)
    df.to_csv(REPORT_DIR / "trajectory_stage_labels_550.csv", index=False)
    return df


def write_outputs(df: pd.DataFrame) -> dict[str, Any]:
    data_quality = {
        "rows": len(df),
        "unique_runs": df["run_id"].nunique(),
        "unique_model_task_pairs": df[["model", "task_id"]].drop_duplicates().shape[0],
        "unique_tasks": df["task_id"].nunique(),
        "trajectory_coverage": int(df["events_available"].sum()),
        "evaluation_coverage": int(df["evaluation_available"].sum()),
        "taxonomy_join_coverage": int(df["taxonomy_version"].notna().sum()),
        "duplicate_run_ids": int(df["run_id"].duplicated().sum()),
        "token_identity_mismatches": int((df["total_tokens"] != df["prompt_tokens"] + df["completion_tokens"]).sum()),
        "oracle_file_manifest_tasks": int(df.groupby("task_id")["closure_code_file_count"].first().gt(0).sum()),
        "clean_install_executed_runs": int(df["submission_install_executed"].sum()),
        "context_window_unique": sorted(df["context_window_tokens"].dropna().astype(int).unique().tolist()),
        "runtime_gold_limit": "closure_gold marks runtime_state and symbol completeness unresolved for the audited task set",
    }
    (REPORT_DIR / "data_quality.json").write_text(json.dumps(data_quality, indent=2, ensure_ascii=False), encoding="utf-8")

    diagnostic_conditions = [
        ("all_runs", pd.Series(True, index=df.index), 0),
        ("correct_entry_file_observed", df["correct_entry_file"], int((~df["correct_entry_file"]).sum())),
        ("correct_symbol_observed", df["correct_symbol"], int((~df["correct_symbol"]).sum())),
        ("key_dependencies_identified", df["key_direct_dependencies_identified"].eq("yes"), int(df["key_direct_dependencies_identified"].eq("unclear").sum())),
        ("independent_implementation", df["independent_implementation"].eq(True), int(df["independent_implementation"].isna().sum())),
        ("public_pass", df["public_pass"].eq(True), int(df["public_pass"].isna().sum())),
        ("hidden_pass", df["hidden_pass"].eq(True), int(df["hidden_pass"].isna().sum())),
        ("formal_pass", df["formal_pass"], 0),
    ]
    cumulative = pd.Series(True, index=df.index)
    funnel_rows = []
    for name, condition, unknown in diagnostic_conditions:
        cumulative &= condition
        funnel_rows.append({"stage": name, "runs": int(cumulative.sum()), "share_of_550": float(cumulative.mean()), "stage_unknown_overall": unknown})
    funnel = pd.DataFrame(funnel_rows)
    funnel.to_csv(REPORT_DIR / "failure_funnel.csv", index=False)

    outcome_conditions = [
        ("all_runs", pd.Series(True, index=df.index)),
        ("evaluator_available", df["evaluation_available"].astype(bool)),
        ("build_pass", df["build_pass"].eq(True)),
        ("public_pass", df["public_pass"].eq(True)),
        ("hidden_pass", df["hidden_pass"].eq(True)),
        ("formal_pass", df["formal_pass"]),
    ]
    cumulative = pd.Series(True, index=df.index)
    outcome_rows = []
    for name, condition in outcome_conditions:
        cumulative &= condition
        outcome_rows.append({"stage": name, "runs": int(cumulative.sum()), "share_of_550": float(cumulative.mean())})
    pd.DataFrame(outcome_rows).to_csv(REPORT_DIR / "outcome_funnel.csv", index=False)

    failures = df[~df["formal_pass"]]
    stage_dist = failures.groupby(["earliest_failure_stage", "primary_hypothesis", "failure_subtype"], dropna=False).agg(
        failures=("run_id", "size"), median_tokens=("total_tokens", "median"),
        median_repeated_reads=("unchanged_repeated_reads", "median"),
        models=("model", "nunique"), tasks=("task_id", "nunique"),
    ).reset_index().sort_values("failures", ascending=False)
    stage_dist["share_of_failures"] = stage_dist["failures"] / len(failures)
    stage_dist["success_rate"] = 0.0
    stage_dist.to_csv(REPORT_DIR / "failure_stage_distribution.csv", index=False)
    by_model = failures.groupby(["model", "earliest_failure_stage"], dropna=False).agg(
        failures=("run_id", "size"), median_tokens=("total_tokens", "median"), tasks=("task_id", "nunique")
    ).reset_index()
    by_model.to_csv(REPORT_DIR / "failure_stage_by_model.csv", index=False)

    dynamic_rows = [rate_row(g, label) for label, g in df.groupby(df["dynamic_runtime_task"].map({True: "dynamic_runtime", False: "relatively_static"}))]
    dynamic_rows += [rate_row(g, f"legacy_{label}") for label, g in df.groupby(df["broad_dynamic_task"].map({True: "dynamic", False: "static"}))]
    dynamic = pd.DataFrame(dynamic_rows)
    dynamic.to_csv(REPORT_DIR / "dynamic_comparison.csv", index=False)
    tier = pd.cut(df["dynamic_mechanism_count"], bins=[-1, 0, 1, np.inf], labels=["0 mechanisms", "1 mechanism", "2+ mechanisms"])
    pd.DataFrame(rate_row(g, str(label)) | {"dynamic_tier": str(label)} for label, g in df.groupby(tier, observed=True)).to_csv(
        REPORT_DIR / "dynamic_tier_comparison.csv", index=False
    )
    dyn_by = pd.DataFrame(
        rate_row(g, f"{model} | {split} | {'dynamic' if dyn else 'static'}")
        | {"model": model, "split": split, "dynamic_runtime_task": dyn}
        for (model, split, dyn), g in df.groupby(["model", "split", "dynamic_runtime_task"])
    )
    dyn_by.to_csv(REPORT_DIR / "dynamic_by_model_split.csv", index=False)

    task_type = pd.DataFrame(
        rate_row(g, label) | {"task_type": label}
        for label, g in df.groupby("entanglement_primary_original")
    ).sort_values("runs", ascending=False)
    task_type.to_csv(REPORT_DIR / "task_type_outcomes.csv", index=False)

    hypothesis_indicators = {
        "H1 localization failure": df["earliest_failure_stage"].eq("localization"),
        "H2 static dependency discovery": df["earliest_failure_stage"].eq("dependency_discovery"),
        "H3 dynamic semantics": df["earliest_failure_stage"].eq("dynamic_semantics"),
        "H4 boundary recovery": df["earliest_failure_stage"].eq("boundary_recovery"),
        "H5 implementation": df["earliest_failure_stage"].eq("implementation"),
        "H6 verification": df["earliest_failure_stage"].eq("verification"),
        "H7 budget/context": df["earliest_failure_stage"].eq("budget_exhaustion"),
    }
    hypothesis = []
    for label, mask in hypothesis_indicators.items():
        affected = df[mask]
        hypothesis.append({
            "hypothesis": label,
            "attributed_failures": len(affected),
            "share_of_all_runs": mask.mean(),
            "share_of_nonpass": mask.sum() / max((~df["formal_pass"]).sum(), 1),
            "median_tokens": affected["total_tokens"].median() if len(affected) else math.nan,
            "models_affected": affected["model"].nunique(),
            "success_rate_with_postoutcome_indicator": 0.0 if len(affected) else math.nan,
            "interpretation_warning": "post-outcome attribution; success rate is tautologically zero and not a risk estimate",
        })
    pd.DataFrame(hypothesis).to_csv(REPORT_DIR / "hypothesis_summary.csv", index=False)

    reg = regression(df)
    reg.to_csv(REPORT_DIR / "regression_results.csv", index=False)
    cases = enrich_cases(select_cases(df))
    cases.to_csv(REPORT_DIR / "representative_cases.csv", index=False)
    write_case_dossiers(cases)

    summary = {
        "data_quality": data_quality,
        "runs": len(df),
        "formal_passes": int(df["formal_pass"].sum()),
        "nonpasses": int((~df["formal_pass"]).sum()),
        "public_pass_hidden_fail": int((df["public_pass"].eq(True) & df["hidden_pass"].eq(False)).sum()),
        "condensation_runs": int(df["condensation_events"].gt(0).sum()),
        "condensation_events": int(df["condensation_events"].sum()),
        "context_truncated_runs": int(df["budget_or_context_truncated"].sum()),
        "memory_loss_candidates": int(df["memory_loss_candidate"].sum()),
        "stage_counts": failures["earliest_failure_stage"].value_counts().to_dict(),
        "dynamic_primary": dynamic[dynamic["group"].isin(["dynamic_runtime", "relatively_static"])].to_dict("records"),
        "regression": reg.to_dict("records"),
    }
    (REPORT_DIR / "analysis_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return summary


def main() -> None:
    df = build()
    summary = write_outputs(df)
    print(json.dumps(summary, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
