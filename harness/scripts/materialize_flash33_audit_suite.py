#!/usr/bin/env python3
"""Materialize Flash-33 Hidden-provenance cases for tool-agent auditing.

Copies only Agent-visible public inputs: TASK.md, redacted metadata with
public_spec, full repository, and one audit_packet.json per failed Hidden
assertion. Does not copy hidden_tests/, public_tests/, or evaluation/.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO / "harness") not in sys.path:
    sys.path.insert(0, str(_REPO / "harness"))

from featureliftbench.agent_runner import redact_task_metadata
from featureliftbench.source_archive import materialize_task_source


DEFAULT_PACKETS = (
    _REPO / "artifacts/research_analysis/hidden_provenance/flash33_packets.json"
)
DEFAULT_TASKS = _REPO / "benchmark" / "python200_tasks"
DEFAULT_OUTPUT = (
    _REPO / "artifacts/research_analysis/agentic_evidence/flash33_suite_v1"
)

INSTRUCTION = (
    "Classify whether this evaluator behavior is explicit, recoverable, "
    "ambiguous, or underdetermined from TASK.md, metadata.public_spec, and "
    "repo/ only. Cite only those public inputs. Do not read Hidden tests, "
    "evaluator assets, or prior provenance labels. Follow the codebook in "
    "docs/HIDDEN_CONTRACT_PROVENANCE.md."
)

_FAILED_BLOCK = re.compile(
    r"^_{3,}\s*(?P<name>\S+)\s*_{3,}\s*\n(?P<body>.*?)(?=^_{3,}|\Z)",
    re.MULTILINE | re.DOTALL,
)


def _json_text(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _safe_case_id(task_id: str, test_name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", test_name).strip("_")
    return f"{task_id}__{cleaned or 'assertion'}"


def _assertion_text(
    *,
    test_name: str,
    stdout: str,
    hidden_source: str,
) -> str:
    """Build a readable observation without Hidden filesystem paths."""

    for match in _FAILED_BLOCK.finditer(stdout or ""):
        if match.group("name") != test_name:
            continue
        body = match.group("body")
        # Drop workspace paths that name hidden_tests/.
        lines = []
        for line in body.splitlines():
            if "hidden_tests" in line or "/workspace/" in line:
                continue
            lines.append(line)
        cleaned = "\n".join(lines).strip()
        if cleaned:
            return cleaned[:2000]
    # Fall back to the test function body if present in the packet source dump.
    pattern = re.compile(
        rf"^def {re.escape(test_name)}\(.*?\n(?:    .*\n)*",
        re.MULTILINE,
    )
    match = pattern.search(hidden_source or "")
    if match:
        body = match.group(0)
        body = re.sub(r"(?im)^# FILE .*$", "", body).strip()
        return (
            f"Evaluator checks the behavior covered by {test_name}:\n{body[:1500]}"
        )
    return f"Evaluator checks the behavior covered by {test_name}."


def _public_metadata(task_dir: Path) -> dict[str, Any]:
    metadata = json.loads((task_dir / "metadata.json").read_text(encoding="utf-8"))
    redacted = redact_task_metadata(metadata, expose_source_hints=False)
    public_spec = metadata.get("public_spec")
    if isinstance(public_spec, dict):
        redacted["public_spec"] = public_spec
    return redacted


def _materialize_case(
    *,
    case_dir: Path,
    task_dir: Path,
    task_id: str,
    test_name: str,
    packet: dict[str, Any],
) -> dict[str, Any]:
    if case_dir.exists():
        shutil.rmtree(case_dir)
    case_dir.mkdir(parents=True, exist_ok=False)
    shutil.copy2(task_dir / "TASK.md", case_dir / "TASK.md")
    (case_dir / "metadata.json").write_text(
        _json_text(_public_metadata(task_dir)),
        encoding="utf-8",
    )
    repo_dest = case_dir / "repo"
    try:
        provenance = materialize_task_source(
            task_id, repo_dest, require_registered=True
        )
    except ValueError:
        provenance = None
    if provenance is None:
        if repo_dest.exists():
            shutil.rmtree(repo_dest)
        local_repo = task_dir / "repo"
        if not local_repo.is_dir():
            raise RuntimeError(f"{task_id}: no repository source available")
        shutil.copytree(local_repo, repo_dest)
    elif not any(path.is_file() for path in repo_dest.rglob("*")):
        if repo_dest.exists():
            shutil.rmtree(repo_dest)
        shutil.copytree(task_dir / "repo", repo_dest)
    audit_packet = {
        "schema_version": "featureliftbench.agentic_evidence.canary_packet.v1",
        "task_id": task_id,
        "nodeid": f"evaluator_assertion::{test_name}",
        "assertion": _assertion_text(
            test_name=test_name,
            stdout=str(packet.get("hidden_stdout_excerpt") or ""),
            hidden_source=str(packet.get("hidden_tests_source") or ""),
        ),
        "instruction": INSTRUCTION,
    }
    (case_dir / "audit_packet.json").write_text(
        _json_text(audit_packet),
        encoding="utf-8",
    )
    # Guard: never ship private evaluator trees.
    for forbidden in ("hidden_tests", "public_tests", "evaluation"):
        if (case_dir / forbidden).exists():
            raise RuntimeError(f"refusing to keep private tree {forbidden} in {case_dir}")
    return {
        "case_id": case_dir.name,
        "task_id": task_id,
        "test_name": test_name,
        "nodeid": audit_packet["nodeid"],
    }


def materialize_suite(
    *,
    packets_path: Path,
    tasks_root: Path,
    output: Path,
) -> dict[str, Any]:
    payload = json.loads(packets_path.read_text(encoding="utf-8"))
    packets = payload.get("packets") or []
    if output.exists() and any(output.iterdir()):
        raise ValueError(f"output already exists and is not empty: {output}")
    cases_root = output / "cases"
    cases_root.mkdir(parents=True, exist_ok=False)
    cases: list[dict[str, Any]] = []
    for packet in packets:
        if not isinstance(packet, dict):
            continue
        task_id = str(packet.get("task_id") or "")
        task_dir = tasks_root / task_id
        if not task_dir.is_dir():
            raise FileNotFoundError(f"missing task package: {task_dir}")
        failed = list(packet.get("failed_hidden_tests") or [])
        if not failed:
            failed = ["unknown_assertion"]
        for test_name in failed:
            case_id = _safe_case_id(task_id, str(test_name))
            row = _materialize_case(
                case_dir=cases_root / case_id,
                task_dir=task_dir,
                task_id=task_id,
                test_name=str(test_name),
                packet=packet,
            )
            cases.append(row)
            print(f"materialized {case_id}")
    manifest = {
        "schema_version": "featureliftbench.agentic_evidence.flash33_suite.v1",
        "slice": payload.get("slice") or "hidden_provenance_flash33_v1",
        "packets_path": str(packets_path.resolve()),
        "tasks_root": str(tasks_root.resolve()),
        "case_count": len(cases),
        "task_count": len({row["task_id"] for row in cases}),
        "cases": cases,
    }
    (output / "suite_manifest.json").write_text(_json_text(manifest), encoding="utf-8")
    return manifest


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packets", type=Path, default=DEFAULT_PACKETS)
    parser.add_argument("--tasks-root", type=Path, default=DEFAULT_TASKS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate an existing suite without regenerating it.",
    )
    return parser


def _check_suite(output: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = output / "suite_manifest.json"
    if not manifest_path.is_file():
        return ["missing suite_manifest.json"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for row in manifest.get("cases") or []:
        case_id = row.get("case_id")
        case_dir = output / "cases" / str(case_id)
        for relative in ("TASK.md", "metadata.json", "audit_packet.json", "repo"):
            if not (case_dir / relative).exists():
                errors.append(f"{case_id}: missing {relative}")
        for forbidden in ("hidden_tests", "public_tests", "evaluation"):
            if (case_dir / forbidden).exists():
                errors.append(f"{case_id}: contains private tree {forbidden}")
        meta = json.loads((case_dir / "metadata.json").read_text(encoding="utf-8"))
        if "public_spec" not in meta:
            errors.append(f"{case_id}: metadata.json missing public_spec")
        packet = json.loads((case_dir / "audit_packet.json").read_text(encoding="utf-8"))
        blob = json.dumps(packet)
        if "hidden_tests/" in blob or "hidden_tests\\" in blob:
            errors.append(f"{case_id}: audit_packet mentions hidden_tests path")
    return errors


def main() -> int:
    args = _parser().parse_args()
    output = args.output.resolve()
    if args.check:
        errors = _check_suite(output)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
        print(f"valid flash33 audit suite: {output}")
        return 0
    manifest = materialize_suite(
        packets_path=args.packets.resolve(),
        tasks_root=args.tasks_root.resolve(),
        output=output,
    )
    errors = _check_suite(output)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(
        f"wrote {manifest['case_count']} flash33 cases "
        f"({manifest['task_count']} tasks) to {output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
