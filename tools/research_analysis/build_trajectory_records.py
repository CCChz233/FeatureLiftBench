#!/usr/bin/env python3
"""Build the auditable FeatureLiftBench trajectory-level research table.

Every available Python OpenHands event trajectory is inventoried.  The primary
analysis corpus is deliberately frozen to seven comparable suites (450 runs):
four DeepSeek suites (core100 + promoted hard50) and three Qwen core100 suites.
Smoke/setup failures and post-hoc reruns remain in the CSV with an explicit
exclusion reason, but are excluded from primary statistics.

Every row is derived from repository files.  Heuristic fields are explicitly
named and accompanied by a confidence/definition column; the script never reads
hidden-test source code when deriving an agent-side trajectory feature.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


PRIMARY_SUITE_RELATIVE_PATHS = (
    "experiments/python/openhands/deepseek-v4-flash/main-flash-20260705-232429",
    "experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260707-113104",
    "experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260707-wave2wave4",
    "experiments/python/openhands/deepseek-v4-flash/batch3-flash-20260708-wave5",
    "experiments/python/openhands/qwen3.6-27b-fp8/qwen36-27b-fp8-main-20260704-001328",
    "experiments/python/openhands/qwen3.6-35b-a3b-fp8/qwen36-35b-a3b-fp8-main-20260704-001313",
    "experiments/python/openhands/qwen3-coder-30b-a3b-instruct/main-20260702-212731",
)


# These six names were not found by the earlier literal TASK.md audit.  The flag
# is a sensitivity-analysis marker, not a claim that the task is unfair.
CONTRACT_REVIEW_TASKS = {
    "cookiecutter__repo_finder_core__hard3_001",
    "dateutil__zone_resolver_core__hard3_001",
    "diskcache__eviction_policy_core__hard3_001",
    "jupyter_server__extension_config_core__hard3_001",
    "mkdocs__plugin_config_core__hard3_001",
    "parsel__selector_namespace_core__hard3_001",
}


REQUIRED_COLUMNS = (
    "task_id",
    "run_id",
    "model",
    "agent",
    "public_pass",
    "hidden_pass",
    "functional_pass",
    "extraction_ratio",
    "final_score",
    "copied_file_count",
    "copied_loc",
    "repeated_file_reads",
    "repeated_line_reads",
    "tool_error_count",
    "harness_format_error_count",
    "closure_plan_present",
    "self_generated_tests",
    "hidden_risk_discussed",
    "stop_reason",
    "primary_failure",
    "secondary_failure",
    "trajectory_path",
    "evaluation_path",
    "evidence_step_ids",
)


EXTRA_COLUMNS = (
    "analysis_included",
    "exclusion_reason",
    "run_kind",
    "suite_id",
    "split",
    "task_type",
    "difficulty",
    "dynamic_state_task",
    "contract_review_required",
    "run_status",
    "build_pass",
    "public_executed",
    "hidden_executed",
    "submission_present",
    "copied_measurement_source",
    "source_loc",
    "total_tokens",
    "prompt_tokens",
    "completion_tokens",
    "api_calls",
    "assistant_steps",
    "tool_call_count",
    "repeated_terminal_commands",
    "public_success_step_id",
    "finish_step_id",
    "unsupported_completion_claim",
    "agent_reasoning_error_count",
    "evaluator_environment_error_count",
    "failure_classification_confidence",
    "failure_flags",
    "metadata_path",
    "run_path",
    "submission_path",
    "events_available",
    "evaluation_available",
)


FIELDNAMES = REQUIRED_COLUMNS + EXTRA_COLUMNS


_DYNAMIC_TERMS = re.compile(
    r"global[_ -]?state|registry|plugin|dynamic|entry[ -]?point|resource|lazy|cache|"
    r"class construction|metaclass",
    re.IGNORECASE,
)
_CLOSURE_TERMS = re.compile(
    r"dependency closure|closure plan|transitive depend|import graph|required files?|"
    r"dependency checklist|api checklist|symbol checklist|runtime depend",
    re.IGNORECASE,
)
_PLAN_TERMS = re.compile(r"\bplan\b|checklist|todo|task list", re.IGNORECASE)
_HIDDEN_RISK_TERMS = re.compile(
    r"hidden tests?|hidden risk|beyond (?:the )?public|edge cases?|behavior[- ]complete|"
    r"unseen cases?|not (?:just|only) public",
    re.IGNORECASE,
)
_COMPLETION_CLAIM_TERMS = re.compile(
    r"public tests? (?:all )?(?:pass|passed)|all tests? (?:pass|passed)|"
    r"tests? (?:are )?passing|successfully extracted|task (?:is )?complete",
    re.IGNORECASE,
)
_HARNESS_FORMAT_TERMS = re.compile(
    r"error validating tool|failed to provide .* field|invalid tool|invalid .*parameter|"
    r"tool schema|security_risk field",
    re.IGNORECASE,
)
_INTERFACE_FAILURE_TERMS = re.compile(
    r"cannot import name|ImportError:|ModuleNotFoundError: No module named ['\"]featurelifted|"
    r"has no attribute|AttributeError:|unexpected keyword argument|"
    r"missing \d+ required positional argument|missing required positional argument|"
    r"takes \d+ positional arguments? but|not exported",
    re.IGNORECASE,
)
_DEPENDENCY_FAILURE_TERMS = re.compile(
    r"ModuleNotFoundError|No module named|cannot import name|ImportError:", re.IGNORECASE
)
_SYNTAX_FAILURE_TERMS = re.compile(
    r"SyntaxError|IndentationError|TabError|invalid syntax", re.IGNORECASE
)
_ISOLATION_FAILURE_TERMS = re.compile(
    r"forbidden import|original repository import|forbidden path|suspicious", re.IGNORECASE
)
_SELF_TEST_PATH = re.compile(
    r"(?:^|/)(?:test|tests|debug|probe|check)[^/]*\.py$", re.IGNORECASE
)


@dataclass
class EventFeatures:
    repeated_file_reads: int = 0
    repeated_line_reads: int = 0
    repeated_terminal_commands: int = 0
    tool_error_count: int = 0
    harness_format_error_count: int = 0
    closure_plan_present: bool = False
    self_generated_tests: bool = False
    hidden_risk_discussed: bool = False
    tool_call_count: int = 0
    public_success_step_id: str = ""
    finish_step_id: str = ""
    completion_claim: bool = False
    completion_signal: bool = False
    evidence_ids: tuple[str, ...] = ()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="FeatureLiftBench repository root",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/research_analysis/trajectory_records.csv"),
        help="Output CSV path (relative paths resolve under --repo-root)",
    )
    parser.add_argument(
        "--suite",
        action="append",
        type=Path,
        default=[],
        help="Override the frozen corpus with one or more suite directories",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if a suite/run/metadata path needed for the frozen corpus is absent",
    )
    return parser.parse_args(argv)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def repo_relative(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, ValueError):
        return path.as_posix()


def as_csv_value(value: Any) -> str | int | float:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return f"{value:.6f}"
    if isinstance(value, (dict, list, tuple, set)):
        if isinstance(value, set):
            value = sorted(value)
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return value


def phase_state(payload: dict[str, Any] | None) -> tuple[bool, bool | None]:
    """Return (executed, passed) without treating a skipped phase as a failure."""
    if not isinstance(payload, dict):
        return False, None
    skipped = bool(payload.get("skipped"))
    if skipped:
        return False, None
    passed = payload.get("passed")
    if isinstance(passed, bool):
        # Older evaluator results serialize downstream phases as
        # ``passed=false, returncode=null`` after dependency setup fails.  Those
        # phases never executed and must not enter a public/hidden denominator.
        executed = bool(
            passed
            or payload.get("returncode") is not None
            or float(payload.get("duration_seconds") or 0.0) > 0.0
            or str(payload.get("reason") or "").strip()
        )
        return (executed, passed if executed else None)
    return False, None


def normalize_view_path(raw: Any, task_run_dir: Path) -> str:
    if not isinstance(raw, str) or not raw.strip():
        return ""
    text = raw.strip().replace("\\", "/")
    task_text = task_run_dir.as_posix().rstrip("/")
    if text.startswith(task_text + "/"):
        return text[len(task_text) + 1 :]
    marker = f"/{task_run_dir.name}/workspace/"
    if marker in text:
        return "workspace/" + text.split(marker, 1)[1]
    return text


def content_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts: list[str] = []
        for item in value:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(parts)
    if isinstance(value, dict):
        return content_text(value.get("content"))
    return ""


def event_agent_text(event: dict[str, Any]) -> str:
    """Agent-authored text only; user task text is intentionally excluded."""
    if event.get("source") != "agent":
        return ""
    parts: list[str] = []
    for key in ("reasoning_content", "thought", "message"):
        parts.append(content_text(event.get(key)))
    action = event.get("action")
    if isinstance(action, dict):
        for key in ("message", "summary", "description"):
            value = action.get(key)
            if isinstance(value, str):
                parts.append(value)
        if action.get("kind") == "TaskTrackerAction":
            parts.append(json.dumps(action, ensure_ascii=False))
    return "\n".join(part for part in parts if part)


def looks_like_public_success(command: str, observation: dict[str, Any]) -> bool:
    if "public_tests" not in command:
        return False
    exit_code = observation.get("exit_code")
    if exit_code == 0:
        return True
    text = content_text(observation.get("content"))
    return bool(re.search(r"\b\d+ passed\b|\bpassed\b.*\bseconds?\b", text, re.IGNORECASE))


def looks_like_self_test_action(action: dict[str, Any], command: str, path: str) -> bool:
    normalized = path.lower()
    if "/repo/" in normalized or "/public_tests/" in normalized:
        return False
    if action.get("kind") == "FileEditorAction" and action.get("command") in {
        "create",
        "str_replace",
        "insert",
    }:
        return bool(_SELF_TEST_PATH.search(path))
    if action.get("kind") == "TerminalAction":
        if "public_tests" in command or "/repo/" in command:
            return False
        return bool(
            re.search(
                r"(?:python|pytest)\s+[^\n]*(?:debug|probe|edge|self[_-]?test|test_[\w.-]+\.py)",
                command,
                re.IGNORECASE,
            )
            or re.search(
                r"(?:>|tee\s+)(?:\S*/)?(?:debug|probe|edge|test_)[\w.-]*\.py",
                command,
                re.IGNORECASE,
            )
        )
    return False


def parse_event_features(events_path: Path, task_run_dir: Path) -> EventFeatures:
    if not events_path.is_file():
        return EventFeatures()

    events: list[dict[str, Any]] = []
    with events_path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                events.append(payload)

    path_seen: Counter[str] = Counter()
    range_seen: Counter[tuple[str, str]] = Counter()
    command_seen: Counter[str] = Counter()
    repeated_file_ids: list[str] = []
    repeated_line_ids: list[str] = []
    tool_error_ids: list[str] = []
    harness_error_ids: list[str] = []
    public_success_ids: list[str] = []
    finish_ids: list[str] = []
    closure_plan_present = False
    self_generated_tests = False
    hidden_risk_discussed = False
    completion_claim = False
    completion_signal = False
    tool_call_count = 0

    action_by_tool_call: dict[str, str] = {}
    for event in events:
        event_id = str(event.get("id") or "")
        kind = event.get("kind")
        action = event.get("action")
        agent_text = event_agent_text(event)

        if isinstance(action, dict):
            tool_call_count += 1
            tool_call_id = event.get("tool_call_id")
            if isinstance(tool_call_id, str) and event_id:
                action_by_tool_call[tool_call_id] = event_id
            action_kind = str(action.get("kind") or "")
            command = str(action.get("command") or "")
            path = normalize_view_path(action.get("path"), task_run_dir)

            if action_kind == "FileEditorAction" and action.get("command") == "view" and path:
                path_seen[path] += 1
                if path_seen[path] > 1 and event_id:
                    repeated_file_ids.append(event_id)
                raw_range = action.get("view_range")
                range_key = json.dumps(raw_range, sort_keys=True, separators=(",", ":"))
                range_seen[(path, range_key)] += 1
                if range_seen[(path, range_key)] > 1 and event_id:
                    repeated_line_ids.append(event_id)

            if action_kind == "TerminalAction" and command:
                canonical_command = " ".join(command.split())
                command_seen[canonical_command] += 1
                if "COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT" in command:
                    completion_signal = True

            if action_kind == "FinishAction":
                if event_id:
                    finish_ids.append(event_id)
                if _COMPLETION_CLAIM_TERMS.search(agent_text):
                    completion_claim = True

            if looks_like_self_test_action(action, command, path):
                self_generated_tests = True

            if action_kind == "TaskTrackerAction" and _CLOSURE_TERMS.search(agent_text):
                closure_plan_present = True

        if agent_text:
            if _HIDDEN_RISK_TERMS.search(agent_text):
                hidden_risk_discussed = True
            if _CLOSURE_TERMS.search(agent_text) and _PLAN_TERMS.search(agent_text):
                closure_plan_present = True
            if _COMPLETION_CLAIM_TERMS.search(agent_text) and isinstance(action, dict) and action.get(
                "kind"
            ) == "FinishAction":
                completion_claim = True

        if kind in {"AgentErrorEvent", "ConversationErrorEvent"}:
            error_text = str(event.get("error") or "")
            if _HARNESS_FORMAT_TERMS.search(error_text):
                if event_id:
                    harness_error_ids.append(event_id)
            elif event_id:
                tool_error_ids.append(event_id)

        observation = event.get("observation")
        if isinstance(observation, dict):
            if observation.get("is_error"):
                if event_id:
                    tool_error_ids.append(event_id)
            command = str(observation.get("command") or "")
            if looks_like_public_success(command, observation):
                linked_id = action_by_tool_call.get(str(event.get("tool_call_id") or ""))
                public_success_ids.append(linked_id or event_id)

    evidence: list[str] = []
    for candidate in (
        (public_success_ids[-1:] if public_success_ids else [])
        + (finish_ids[-1:] if finish_ids else [])
        + tool_error_ids[:2]
        + harness_error_ids[:2]
        + repeated_file_ids[:2]
        + repeated_line_ids[:2]
    ):
        if candidate and candidate not in evidence:
            evidence.append(candidate)

    return EventFeatures(
        repeated_file_reads=sum(max(count - 1, 0) for count in path_seen.values()),
        repeated_line_reads=sum(max(count - 1, 0) for count in range_seen.values()),
        repeated_terminal_commands=sum(max(count - 1, 0) for count in command_seen.values()),
        tool_error_count=len(tool_error_ids),
        harness_format_error_count=len(harness_error_ids),
        closure_plan_present=closure_plan_present,
        self_generated_tests=self_generated_tests,
        hidden_risk_discussed=hidden_risk_discussed,
        tool_call_count=tool_call_count,
        public_success_step_id=public_success_ids[-1] if public_success_ids else "",
        finish_step_id=finish_ids[-1] if finish_ids else "",
        completion_claim=completion_claim,
        completion_signal=completion_signal,
        evidence_ids=tuple(evidence[:12]),
    )


def read_eval_logs(eval_dir: Path) -> dict[str, str]:
    groups = {
        "build": ("build.stdout", "build.stderr"),
        "public": ("public.stdout", "public.stderr"),
        "hidden": ("hidden.stdout", "hidden.stderr"),
        "dependency": ("dependency_install.stdout", "dependency_install.stderr"),
        "tooling": ("eval_tooling.stdout", "eval_tooling.stderr"),
    }
    result: dict[str, str] = {}
    logs_dir = eval_dir / "logs"
    for group, names in groups.items():
        chunks: list[str] = []
        for name in names:
            path = logs_dir / name
            if path.is_file():
                chunks.append(path.read_text(encoding="utf-8", errors="replace"))
        result[group] = "\n".join(chunks)
    return result


def evaluator_environment_errors(result: dict[str, Any]) -> tuple[int, list[str]]:
    flags: list[str] = []
    for key in ("dependency_install", "eval_tooling"):
        phase = result.get(key)
        if isinstance(phase, dict) and phase.get("passed") is False and not phase.get("skipped"):
            flags.append(f"{key}_failed")
    sandbox = result.get("sandbox")
    if isinstance(sandbox, dict):
        if sandbox.get("docker_sandbox_error"):
            flags.append("docker_sandbox_error")
        if sandbox.get("resource_limited"):
            flags.append("eval_resource_limited")
        if sandbox.get("log_limit_exceeded"):
            flags.append("eval_log_limit_exceeded")
    for key in ("build", "public_tests", "hidden_tests"):
        phase = result.get(key)
        if not isinstance(phase, dict):
            continue
        if phase.get("resource_limited"):
            # A submission can exhaust the evaluator limit.  Preserve the flag
            # for failure analysis, but do not call it infrastructure noise.
            continue
        if phase.get("log_limit_exceeded"):
            continue
        if phase.get("timed_out"):
            continue
    return len(flags), flags


def classify_failure(
    *,
    status: str,
    functional_pass: bool,
    submission_present: bool,
    build_pass: bool | None,
    public_pass: bool | None,
    hidden_pass: bool | None,
    extraction_ratio: float | None,
    result: dict[str, Any],
    logs: dict[str, str],
    event_features: EventFeatures,
    agent_exit_status: str,
    evaluator_flags: list[str],
) -> tuple[str, str, str, list[str]]:
    flags: list[str] = []
    if extraction_ratio is not None and extraction_ratio <= 0.25:
        flags.append("low_extraction_ratio_proxy")
    if extraction_ratio is not None and extraction_ratio > 0.80:
        flags.append("high_extraction_ratio_proxy")
    if event_features.repeated_file_reads or event_features.repeated_line_reads:
        flags.append("repeated_exploration")
    if event_features.tool_error_count:
        flags.append("tool_execution_errors")
    if event_features.harness_format_error_count:
        flags.append("harness_format_errors")
    if agent_exit_status == "step_limit_exceeded":
        flags.append("agent_step_limit")
    for phase_name in ("build", "public_tests", "hidden_tests"):
        phase = result.get(phase_name)
        if not isinstance(phase, dict):
            continue
        if phase.get("resource_limited"):
            flags.append(f"submission_{phase_name}_resource_limited")
        if phase.get("log_limit_exceeded"):
            flags.append(f"submission_{phase_name}_log_limit_exceeded")
        if phase.get("timed_out"):
            flags.append(f"submission_{phase_name}_timed_out")
    flags.extend(evaluator_flags)

    if functional_pass:
        secondary = "high_extraction_ratio_proxy" if "high_extraction_ratio_proxy" in flags else "none"
        return "passed", secondary, "high", flags

    if evaluator_flags:
        secondary = "agent_step_limit" if "agent_step_limit" in flags else "none"
        return "evaluator_or_environment_error", secondary, "high", flags

    if not submission_present or status == "missing_submission":
        if event_features.harness_format_error_count:
            secondary = "harness_format_error"
        elif agent_exit_status == "step_limit_exceeded":
            secondary = "agent_step_limit"
        else:
            secondary = "agent_workflow_failure"
        return "missing_submission", secondary, "high", flags

    build_text = logs.get("build", "")
    public_text = logs.get("public", "")
    hidden_text = logs.get("hidden", "")
    all_text = "\n".join((build_text, public_text, hidden_text, "\n".join(map(str, result.get("errors") or []))))

    if build_pass is False:
        if _SYNTAX_FAILURE_TERMS.search(build_text):
            primary, confidence = "build_syntax_or_version_failure", "high"
        elif _DEPENDENCY_FAILURE_TERMS.search(build_text):
            primary, confidence = "dependency_closure_omission", "medium"
        elif result.get("original_import_pass") is False or _ISOLATION_FAILURE_TERMS.search(all_text):
            primary, confidence = "isolation_or_forbidden_import_failure", "high"
        else:
            primary, confidence = "packaging_or_build_failure", "medium"
    elif result.get("original_import_pass") is False or _ISOLATION_FAILURE_TERMS.search(all_text):
        primary, confidence = "isolation_or_forbidden_import_failure", "high"
    elif public_pass is False:
        if _INTERFACE_FAILURE_TERMS.search(public_text):
            primary, confidence = "public_api_or_interface_failure", "medium"
        else:
            primary, confidence = "public_behavior_failure", "medium"
    elif public_pass is True and hidden_pass is False:
        if _INTERFACE_FAILURE_TERMS.search(hidden_text):
            primary, confidence = "hidden_interface_or_closure_failure", "medium"
        else:
            primary, confidence = "hidden_behavior_contract_failure", "medium"
    elif status == "failed":
        primary, confidence = "unclassified_evaluation_failure", "low"
    else:
        primary, confidence = "unknown_failure", "low"

    if event_features.completion_claim and primary not in {
        "evaluator_or_environment_error",
        "unknown_failure",
    }:
        flags.append("unsupported_completion_claim")

    secondary_candidates = [
        "agent_step_limit",
        "harness_format_errors",
        "tool_execution_errors",
        "low_extraction_ratio_proxy",
        "high_extraction_ratio_proxy",
        "repeated_exploration",
    ]
    secondary = next((name for name in secondary_candidates if name in flags), "none")
    return primary, secondary, confidence, flags


def locate_task_dir(repo_root: Path, task_id: str) -> Path | None:
    for base in ("benchmark/tasks", "benchmark/batch3_pilot", "benchmark/staging", "benchmark/sanity"):
        candidate = repo_root / base / task_id
        if (candidate / "metadata.json").is_file():
            return candidate
    return None


def task_metadata(repo_root: Path, task_id: str) -> tuple[Path | None, dict[str, Any]]:
    task_dir = locate_task_dir(repo_root, task_id)
    if task_dir is None:
        return None, {}
    return task_dir, load_json(task_dir / "metadata.json")


def dynamic_state_task(metadata: dict[str, Any]) -> bool:
    entanglement = metadata.get("entanglement")
    # Restrict this audit slice to the entanglement annotation.  Searching the
    # whole feature contract made every task match the boilerplate phrase
    # "original package import at runtime", which is not evidence of a dynamic
    # state dependency.
    payload = json.dumps(
        {
            "entanglement": entanglement if isinstance(entanglement, dict) else {},
            "tags": metadata.get("tags") or [],
        },
        ensure_ascii=False,
    )
    return bool(_DYNAMIC_TERMS.search(payload))


def infer_split(suite_dir: Path, task_id: str) -> str:
    if "batch3" in suite_dir.name or "hard3" in task_id:
        return "hard50"
    return "core100"


def fallback_submission_metrics(submission_dir: Path) -> tuple[int | None, int | None]:
    if not submission_dir.is_dir():
        return None, None
    files = [path for path in submission_dir.rglob("*") if path.is_file()]
    loc = 0
    for path in files:
        try:
            loc += len(path.read_text(encoding="utf-8", errors="replace").splitlines())
        except OSError:
            continue
    return len(files), loc


def build_row(
    repo_root: Path,
    suite_dir: Path,
    suite: dict[str, Any],
    suite_run: dict[str, Any],
    *,
    task_run_dir: Path | None = None,
    analysis_included: bool = True,
    exclusion_reason: str = "",
    run_kind: str = "frozen_primary",
) -> dict[str, Any]:
    task_id = str(suite_run.get("task_id") or "")
    task_run_dir = task_run_dir or suite_dir / task_id
    run_path = task_run_dir / "run.json"
    run = load_json(run_path) if run_path.is_file() else {}

    evaluation_path = task_run_dir / "eval" / "result.json"
    result = load_json(evaluation_path) if evaluation_path.is_file() else {}
    events_path = task_run_dir / "agent" / "openhands_events.jsonl"
    event_features = parse_event_features(events_path, task_run_dir)

    task_dir, metadata = task_metadata(repo_root, task_id)
    entanglement = metadata.get("entanglement") if isinstance(metadata.get("entanglement"), dict) else {}
    task_type = str(entanglement.get("primary") or "unknown")
    difficulty = str(metadata.get("difficulty") or "unknown")

    evaluation = run.get("evaluation") if isinstance(run.get("evaluation"), dict) else {}
    scores = result.get("scores") if isinstance(result.get("scores"), dict) else {}
    if not scores:
        scores = evaluation.get("scores") if isinstance(evaluation.get("scores"), dict) else {}
    metrics = result.get("metrics") if isinstance(result.get("metrics"), dict) else {}

    public_executed, public_pass = phase_state(result.get("public_tests"))
    hidden_executed, hidden_pass = phase_state(result.get("hidden_tests"))
    build_executed, build_pass = phase_state(result.get("build"))
    if not build_executed and isinstance(evaluation.get("build_pass"), bool):
        build_pass = evaluation.get("build_pass")

    status = str(run.get("status") or suite_run.get("status") or "unknown")
    functional_gate = scores.get("functional_gate")
    if isinstance(functional_gate, (int, float)):
        functional_pass = float(functional_gate) == 1.0
    elif result:
        functional_pass = bool(result.get("status") == "passed" or result.get("test_pass") is True)
    else:
        functional_pass = status == "passed"

    extraction_ratio = scores.get("extraction_ratio")
    if not isinstance(extraction_ratio, (int, float)):
        extraction_ratio = None
    final_score = scores.get("final_score", suite_run.get("final_score"))
    if not isinstance(final_score, (int, float)):
        final_score = None

    submission_info = run.get("submission") if isinstance(run.get("submission"), dict) else {}
    submission_dir = task_run_dir / "submission"
    if not submission_dir.is_dir():
        workspace_submission = task_run_dir / "workspace" / "submission"
        if workspace_submission.is_dir():
            submission_dir = workspace_submission
    submission_present = bool(submission_info.get("exists")) or submission_dir.is_dir()

    copied_file_count = metrics.get("file_count")
    copied_loc = metrics.get("loc")
    measurement_source = "eval.metrics submission footprint"
    if not isinstance(copied_file_count, int) or not isinstance(copied_loc, int):
        copied_file_count, copied_loc = fallback_submission_metrics(submission_dir)
        measurement_source = "filesystem submission footprint fallback"

    usage = {}
    agent_payload = run.get("agent") if isinstance(run.get("agent"), dict) else {}
    if isinstance(agent_payload.get("usage"), dict):
        usage = agent_payload["usage"]
    if not usage:
        usage_path = task_run_dir / "agent" / "usage.json"
        if usage_path.is_file():
            usage = load_json(usage_path)

    model = str(
        (suite.get("agent_config") or {}).get("model")
        if isinstance(suite.get("agent_config"), dict)
        else ""
    )
    if not model:
        model = str(usage.get("model") or "unknown")
    agent_name = str(suite.get("agent") or agent_payload.get("name") or "unknown")
    agent_exit_status = str(usage.get("exit_status") or "")

    logs = read_eval_logs(task_run_dir / "eval")
    evaluator_error_count, evaluator_flags = evaluator_environment_errors(result)
    primary, secondary, classification_confidence, failure_flags = classify_failure(
        status=status,
        functional_pass=functional_pass,
        submission_present=submission_present,
        build_pass=build_pass,
        public_pass=public_pass,
        hidden_pass=hidden_pass,
        extraction_ratio=float(extraction_ratio) if extraction_ratio is not None else None,
        result=result,
        logs=logs,
        event_features=event_features,
        agent_exit_status=agent_exit_status,
        evaluator_flags=evaluator_flags,
    )

    unsupported_completion_claim = bool(
        event_features.completion_claim
        and not functional_pass
        and not evaluator_flags
    )
    reasoning_error_count = 1 if unsupported_completion_claim else 0

    if event_features.finish_step_id:
        stop_reason = "explicit_finish"
    elif event_features.completion_signal:
        stop_reason = "completion_signal"
    elif agent_exit_status == "step_limit_exceeded":
        stop_reason = "step_limit_exceeded"
    elif agent_exit_status == "timeout" or agent_payload.get("timed_out"):
        stop_reason = "timeout"
    elif status == "missing_submission":
        stop_reason = "missing_submission_after_agent_exit"
    elif agent_exit_status:
        stop_reason = f"agent_exit:{agent_exit_status}"
    elif agent_payload.get("returncode") is not None:
        stop_reason = f"process_returncode:{agent_payload.get('returncode')}"
    else:
        stop_reason = "unknown"

    evidence_ids = list(event_features.evidence_ids)
    if build_pass is False:
        evidence_ids.append("eval:build")
    if public_pass is False:
        evidence_ids.append("eval:public_tests")
    if hidden_pass is False:
        evidence_ids.append("eval:hidden_tests")
    if evaluator_flags:
        evidence_ids.extend(f"eval:{flag}" for flag in evaluator_flags[:2])
    evidence_ids = list(dict.fromkeys(evidence_ids))[:14]

    run_id = repo_relative(task_run_dir, repo_root)
    source_loc = metrics.get("source_loc")

    row: dict[str, Any] = {
        "task_id": task_id,
        "run_id": run_id,
        "model": model,
        "agent": agent_name,
        "public_pass": public_pass,
        "hidden_pass": hidden_pass,
        "functional_pass": functional_pass,
        "extraction_ratio": extraction_ratio,
        "final_score": final_score,
        "copied_file_count": copied_file_count,
        "copied_loc": copied_loc,
        "repeated_file_reads": event_features.repeated_file_reads,
        "repeated_line_reads": event_features.repeated_line_reads,
        "tool_error_count": event_features.tool_error_count,
        "harness_format_error_count": event_features.harness_format_error_count,
        "closure_plan_present": event_features.closure_plan_present,
        "self_generated_tests": event_features.self_generated_tests,
        "hidden_risk_discussed": event_features.hidden_risk_discussed,
        "stop_reason": stop_reason,
        "primary_failure": primary,
        "secondary_failure": secondary,
        "trajectory_path": repo_relative(events_path, repo_root),
        "evaluation_path": repo_relative(evaluation_path, repo_root),
        "evidence_step_ids": evidence_ids,
        "analysis_included": analysis_included,
        "exclusion_reason": exclusion_reason,
        "run_kind": run_kind,
        "suite_id": repo_relative(suite_dir, repo_root),
        "split": infer_split(suite_dir, task_id),
        "task_type": task_type,
        "difficulty": difficulty,
        "dynamic_state_task": dynamic_state_task(metadata),
        "contract_review_required": task_id in CONTRACT_REVIEW_TASKS,
        "run_status": status,
        "build_pass": build_pass,
        "public_executed": public_executed,
        "hidden_executed": hidden_executed,
        "submission_present": submission_present,
        "copied_measurement_source": measurement_source,
        "source_loc": source_loc,
        "total_tokens": usage.get("total_tokens"),
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "api_calls": usage.get("api_calls"),
        "assistant_steps": usage.get("assistant_steps"),
        "tool_call_count": event_features.tool_call_count,
        "repeated_terminal_commands": event_features.repeated_terminal_commands,
        "public_success_step_id": event_features.public_success_step_id,
        "finish_step_id": event_features.finish_step_id,
        "unsupported_completion_claim": unsupported_completion_claim,
        "agent_reasoning_error_count": reasoning_error_count,
        "evaluator_environment_error_count": evaluator_error_count,
        "failure_classification_confidence": classification_confidence,
        "failure_flags": failure_flags,
        "metadata_path": repo_relative(task_dir / "metadata.json", repo_root) if task_dir else "",
        "run_path": repo_relative(run_path, repo_root) if run_path.is_file() else "",
        "submission_path": repo_relative(submission_dir, repo_root),
        "events_available": events_path.is_file(),
        "evaluation_available": evaluation_path.is_file(),
    }
    return {key: as_csv_value(row.get(key)) for key in FIELDNAMES}


def validate_rows(rows: list[dict[str, Any]], strict: bool) -> None:
    if not rows:
        raise ValueError("no trajectory rows were produced")
    run_ids = [str(row["run_id"]) for row in rows]
    duplicates = sorted(key for key, count in Counter(run_ids).items() if count > 1)
    if duplicates:
        raise ValueError(f"duplicate run_id values: {duplicates[:5]}")
    missing_required = {
        column: sum(1 for row in rows if row.get(column) in (None, ""))
        for column in REQUIRED_COLUMNS
    }
    structural = (
        "task_id",
        "run_id",
        "model",
        "agent",
        "functional_pass",
        "trajectory_path",
        "evaluation_path",
        "primary_failure",
    )
    bad = {column: missing_required[column] for column in structural if missing_required[column]}
    if bad and strict:
        raise ValueError(f"missing structural fields: {bad}")


def resolve_suites(repo_root: Path, overrides: Iterable[Path]) -> list[Path]:
    override_list = list(overrides)
    if override_list:
        return [path if path.is_absolute() else repo_root / path for path in override_list]
    return [repo_root / relative for relative in PRIMARY_SUITE_RELATIVE_PATHS]


def infer_task_id_from_run_dir(task_run_dir: Path) -> str:
    run_path = task_run_dir / "run.json"
    if run_path.is_file():
        task_id = load_json(run_path).get("task_id")
        if isinstance(task_id, str) and task_id:
            return task_id
    metadata_path = task_run_dir / "workspace" / "metadata.json"
    if metadata_path.is_file():
        task_id = load_json(metadata_path).get("task_id")
        if isinstance(task_id, str) and task_id:
            return task_id
    if task_run_dir.name and not task_run_dir.name.startswith("."):
        return task_run_dir.name
    task_path = task_run_dir / "workspace" / "TASK.md"
    if task_path.is_file():
        match = re.search(r"FeatureLiftBench Task:\s*([^\s]+)", task_path.read_text(encoding="utf-8"))
        if match:
            return match.group(1)
    return f"unknown::{task_run_dir.name or 'trajectory'}"


def supplemental_exclusion_reason(task_run_dir: Path) -> tuple[str, str]:
    text = task_run_dir.as_posix()
    if "batch3-pydantic-rerun" in text:
        return "post_hoc_rerun", "supplemental_rerun"
    if "batch3-flash-20260707-112646" in text:
        return "agent_setup_failure_suite", "setup_failure"
    return "smoke_or_local_calibration", "smoke_or_local"


def supplemental_suite_payload(task_run_dir: Path, task_id: str) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    parent_suite = task_run_dir.parent
    suite_path = parent_suite / "suite.json"
    if suite_path.is_file():
        suite = load_json(suite_path)
        for item in suite.get("runs") or []:
            if isinstance(item, dict) and item.get("task_id") == task_id:
                return parent_suite, suite, item
        return parent_suite, suite, {"task_id": task_id}

    run_path = task_run_dir / "run.json"
    run = load_json(run_path) if run_path.is_file() else {}
    agent_config = run.get("agent_config") if isinstance(run.get("agent_config"), dict) else {}
    agent = run.get("agent") if isinstance(run.get("agent"), dict) else {}
    usage_path = task_run_dir / "agent" / "usage.json"
    usage = load_json(usage_path) if usage_path.is_file() else {}
    model = str(agent_config.get("model") or usage.get("model") or "")
    if not model:
        model = "deepseek/deepseek-v4-flash" if "deepseek-v4-flash" in task_run_dir.as_posix() else "unknown"
    suite = {
        "agent": agent.get("name") or "openhands-agent",
        "agent_config": {"model": model},
    }
    return task_run_dir, suite, {"task_id": task_id, "status": run.get("status") or "unknown"}


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = args.repo_root.resolve()
    output = args.output if args.output.is_absolute() else repo_root / args.output
    suite_dirs = resolve_suites(repo_root, args.suite)

    rows: list[dict[str, Any]] = []
    missing: list[str] = []
    inventoried_event_paths: set[Path] = set()
    for suite_dir in suite_dirs:
        suite_path = suite_dir / "suite.json"
        if not suite_path.is_file():
            missing.append(repo_relative(suite_path, repo_root))
            continue
        suite = load_json(suite_path)
        runs = suite.get("runs")
        if not isinstance(runs, list):
            raise ValueError(f"suite has no runs list: {suite_path}")
        for suite_run in runs:
            if not isinstance(suite_run, dict):
                continue
            task_id = suite_run.get("task_id")
            if not isinstance(task_id, str) or not task_id:
                continue
            run_path = suite_dir / task_id / "run.json"
            if not run_path.is_file() and args.strict:
                missing.append(repo_relative(run_path, repo_root))
            task_run_dir = suite_dir / task_id
            rows.append(build_row(repo_root, suite_dir, suite, suite_run, task_run_dir=task_run_dir))
            inventoried_event_paths.add(
                (task_run_dir / "agent" / "openhands_events.jsonl").resolve()
            )

    # With the default frozen corpus, retain every other available trajectory as
    # a supplementary inventory row.  Overrides intentionally describe a custom
    # corpus and therefore do not trigger repository-wide discovery.
    if not args.suite:
        events_root = repo_root / "experiments" / "python" / "openhands"
        for events_path in sorted(events_root.glob("**/agent/openhands_events.jsonl")):
            if events_path.resolve() in inventoried_event_paths:
                continue
            task_run_dir = events_path.parent.parent
            task_id = infer_task_id_from_run_dir(task_run_dir)
            suite_dir, suite, suite_run = supplemental_suite_payload(task_run_dir, task_id)
            exclusion_reason, run_kind = supplemental_exclusion_reason(task_run_dir)
            rows.append(
                build_row(
                    repo_root,
                    suite_dir,
                    suite,
                    suite_run,
                    task_run_dir=task_run_dir,
                    analysis_included=False,
                    exclusion_reason=exclusion_reason,
                    run_kind=run_kind,
                )
            )

    if missing and args.strict:
        raise FileNotFoundError("missing frozen corpus inputs:\n" + "\n".join(missing))

    rows.sort(
        key=lambda row: (
            str(row["analysis_included"]) != "true",
            str(row["model"]),
            str(row["suite_id"]),
            str(row["task_id"]),
        )
    )
    validate_rows(rows, strict=args.strict)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {len(rows)} rows to {output}")
    print(f"columns: {len(FIELDNAMES)} ({len(REQUIRED_COLUMNS)} required + {len(EXTRA_COLUMNS)} audit)")
    if missing:
        print(f"warning: {len(missing)} expected inputs were absent", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
