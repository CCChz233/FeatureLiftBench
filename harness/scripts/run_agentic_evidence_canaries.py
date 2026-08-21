#!/usr/bin/env python3
"""Run one evidence-auditor Agent over an opaque canary suite."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO / "harness"))

from featureliftbench.agent_adapters import AgentRunConfig
from featureliftbench.agent_adapters import AgentRunContext
from featureliftbench.agent_adapters import get_agent_adapter
from featureliftbench.agent_config import load_agent_run_config
from featureliftbench.agentic_evidence.citation_validator import build_citation
from featureliftbench.agentic_evidence.citation_validator import validate_citation
from featureliftbench.agentic_evidence.direct_auditor import coerce_confidence
from featureliftbench.agentic_evidence.prompts import auditor_prompt
from featureliftbench.agentic_evidence.schema import validate_audit_record


def _tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if (
            relative in {"AGENTIC_AUDIT.md"}
            or relative.startswith("submission/")
            or relative.startswith("agent_output/")
        ):
            continue
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _repair_citations(
    workspace: Path,
    values: Any,
) -> list[dict[str, Any]]:
    if not isinstance(values, list):
        return []
    repaired: list[dict[str, Any]] = []
    for value in values:
        if not isinstance(value, dict):
            continue
        try:
            path = str(value.get("path") or "")
            kind = str(value.get("kind") or "")
            if path == "TASK.md":
                kind = "task"
            elif path == "metadata.json":
                kind = "public_spec"
            elif path.startswith("repo/"):
                kind = "repository"
            repaired.append(
                build_citation(
                    workspace,
                    path=path,
                    kind=kind,
                    start_line=int(value["start_line"]),
                    end_line=int(value["end_line"]),
                    claim=str(value.get("claim") or ""),
                    clamp=True,
                )
            )
        except (KeyError, TypeError, ValueError, OSError, UnicodeError):
            repaired.append(value)
    return repaired


def _repair_record(record: dict[str, Any], *, workspace: Path) -> dict[str, Any]:
    fixed = dict(record)
    fixed["confidence"] = coerce_confidence(fixed.get("confidence"))
    fixed["evidence"] = _repair_citations(workspace, fixed.get("evidence") or [])
    fixed["counterevidence"] = _repair_citations(
        workspace, fixed.get("counterevidence") or []
    )
    return fixed


def _validate_record(
    record_path: Path,
    *,
    workspace: Path,
    case_id: str,
    agent_id: str,
) -> tuple[dict[str, Any] | None, list[str]]:
    if not record_path.is_file():
        return None, ["Agent did not create audit_record.json"]
    try:
        record = json.loads(record_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, [f"invalid audit_record.json: {exc}"]
    if not isinstance(record, dict):
        return None, ["audit_record.json must be an object"]
    record = _repair_record(record, workspace=workspace)
    errors = validate_audit_record(record)
    expected_task_id = case_id
    expected_nodeid: str | None = None
    packet_path = workspace / "audit_packet.json"
    if packet_path.is_file():
        try:
            packet = json.loads(packet_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            packet = None
        if isinstance(packet, dict):
            if packet.get("task_id"):
                expected_task_id = str(packet["task_id"])
            if packet.get("nodeid"):
                expected_nodeid = str(packet["nodeid"])
    if record.get("task_id") not in {case_id, expected_task_id}:
        errors.append(
            f"task_id mismatch: expected {expected_task_id!r} or {case_id!r}, "
            f"got {record.get('task_id')!r}"
        )
    if record.get("agent_id") != agent_id:
        errors.append(
            f"agent_id mismatch: expected {agent_id!r}, got {record.get('agent_id')!r}"
        )
    if expected_nodeid is not None and record.get("nodeid") != expected_nodeid:
        errors.append(
            f"nodeid mismatch: expected {expected_nodeid!r}, "
            f"got {record.get('nodeid')!r}"
        )
    for citation in (record.get("evidence") or []) + (
        record.get("counterevidence") or []
    ):
        for error in validate_citation(workspace, citation):
            errors.append(f"citation: {error}")
    if not errors:
        record_path.write_text(
            json.dumps(record, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return record, sorted(set(errors))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("suite", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--agent", default="mini-swe-agent")
    parser.add_argument("--agent-profile")
    parser.add_argument("--agent-config", type=Path)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--model")
    parser.add_argument("--agent-bin")
    parser.add_argument("--agent-command")
    parser.add_argument("--timeout-seconds", type=int, default=900)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--agent-id")
    return parser


def main() -> int:
    args = _parser().parse_args()
    cases_root = args.suite.resolve() / "cases"
    if not cases_root.is_dir():
        print(f"missing canary cases directory: {cases_root}", file=sys.stderr)
        return 2
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()) and not args.resume:
        print(
            f"output already exists and is not empty: {output}; pass --resume",
            file=sys.stderr,
        )
        return 2
    output.mkdir(parents=True, exist_ok=True)

    base = AgentRunConfig(
        agent=args.agent,
        agent_bin=args.agent_bin,
        model=args.model,
        yolo=True,
        timeout_seconds=args.timeout_seconds,
        command=args.agent_command,
    )
    try:
        loaded = load_agent_run_config(
            base_config=base,
            config_path=args.agent_config,
            profile_name=args.agent_profile,
            env_file=args.env_file,
        )
        adapter = get_agent_adapter(loaded.run_config.agent)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    agent_id = args.agent_id or (
        f"{args.agent_profile or loaded.run_config.model or loaded.run_config.agent}-auditor-r1"
    )
    case_dirs = sorted(path for path in cases_root.iterdir() if path.is_dir())
    if args.limit is not None:
        case_dirs = case_dirs[: max(0, args.limit)]
    results: list[dict[str, Any]] = []
    for case_dir in case_dirs:
        case_id = case_dir.name
        case_output = output / case_id
        record_path = case_output / "audit_record.json"
        validation_path = case_output / "validation.json"
        if args.resume and validation_path.is_file():
            existing = json.loads(validation_path.read_text(encoding="utf-8"))
            if existing.get("valid"):
                results.append(existing)
                continue
        case_output.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=f"flb-audit-{case_id}-") as tmp:
            workspace = Path(tmp) / "workspace"
            shutil.copytree(case_dir, workspace)
            (workspace / "submission").mkdir()
            temporary_agent_output = workspace / "agent_output"
            temporary_agent_output.mkdir()
            task_file = workspace / "AGENTIC_AUDIT.md"
            prompt = auditor_prompt(agent_id=agent_id)
            task_file.write_text(prompt, encoding="utf-8")
            before = _tree_digest(workspace)
            context = AgentRunContext(
                workspace_dir=workspace,
                task_file=task_file,
                submission_dir=workspace / "submission",
                agent_output_dir=temporary_agent_output,
                task_text=prompt,
            )
            result = adapter.run(
                context,
                loaded.run_config,
                stdout_log=case_output / "agent.stdout.log",
                stderr_log=case_output / "agent.stderr.log",
            )
            after = _tree_digest(workspace)
            temporary_record_path = temporary_agent_output / "audit_record.json"
            record, errors = _validate_record(
                temporary_record_path,
                workspace=workspace,
                case_id=case_id,
                agent_id=agent_id,
            )
            if temporary_record_path.is_file():
                shutil.copy2(temporary_record_path, record_path)
            if before != after:
                errors.append("Agent modified public audit inputs")
            validation = {
                "case_id": case_id,
                "agent_id": agent_id,
                "valid": not errors,
                "errors": sorted(set(errors)),
                "source_tree_unchanged": before == after,
                "agent_result": result.payload(
                    stdout_log=case_output / "agent.stdout.log",
                    stderr_log=case_output / "agent.stderr.log",
                ),
                "record_verdict": record.get("verdict") if record else None,
            }
            validation_path.write_text(
                json.dumps(validation, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            results.append(validation)
            print(
                f"{case_id}: {'valid' if validation['valid'] else 'invalid'} "
                f"verdict={validation['record_verdict']}"
            )
    summary = {
        "schema_version": "featureliftbench.agentic_evidence.canary_run.v1",
        "suite": str(args.suite.resolve()),
        "agent_id": agent_id,
        "agent_config": loaded.summary,
        "case_count": len(results),
        "valid_count": sum(bool(row.get("valid")) for row in results),
        "results": results,
    }
    (output / "run.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return 0 if summary["valid_count"] == summary["case_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
