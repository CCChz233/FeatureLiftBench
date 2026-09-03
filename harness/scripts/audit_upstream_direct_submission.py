#!/usr/bin/env python3
"""G2' — the unmodified pinned upstream, submitted directly, must not pass.

The existing G2 gate compares against a pre-built ``benchmark/submissions/<id>/naive``
tree, which exists for only part of the suite and is authored by hand. This audit
instead builds the submission *mechanically* from the task's own pinned ``repo/``:
a ``featurelifted`` package that re-exports upstream under the declared
``required_api`` and nothing else. That submission is then evaluated in the pinned
evaluator.

A task whose contract is satisfied by verbatim upstream re-export is not a feature
extraction task, so ``functional_gate == 1.0`` here is a blocking benchmark defect.
Any other outcome clears the gate.

Evidence strength is recorded separately from the verdict. When the task invents
names that the pinned upstream does not define, ``build_shim`` stubs them and the
submission cannot pass for reasons unrelated to behavior, so the clear is marked
``reshaped`` rather than treated as strong evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HARNESS = ROOT / "harness"
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))

from featureliftbench.docker_eval import evaluate_submission_docker  # noqa: E402


SCHEMA_VERSION = "featureliftbench.upstream_direct_submission_audit.v1"
GATE_ID = "G2_PRIME_UPSTREAM_DIRECT"
DEFAULT_OUTPUT = ROOT / "reports" / "audits" / "python200_prime_g2prime"
DEFAULT_TASK_ROOT = ROOT / "benchmark" / "python200_hard_tasks"
DEFAULT_IMAGE = os.environ.get(
    "FEATURELIFTBENCH_EVAL_DOCKER_IMAGE", "featureliftbench-eval:latest"
)
SOURCE_REGISTRY = ROOT / "benchmark" / "sources" / "python200_hard_registry.json"
REFERENCE_REGISTRY = (
    ROOT / "benchmark" / "references" / "python200_prime_compactness.json"
)

PASS = "pass"
FAIL = "fail"
UNDETERMINED = "undetermined"


def _load_entailment_module() -> Any:
    """Import the C3 audit as a module to reuse its upstream shim builder."""
    path = HARNESS / "scripts" / "audit_contract_entailment.py"
    spec = importlib.util.spec_from_file_location("flb_contract_entailment", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ENTAILMENT = _load_entailment_module()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks-root", type=Path, default=DEFAULT_TASK_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--image", default=DEFAULT_IMAGE)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--task-id", action="append", dest="task_ids")
    parser.add_argument(
        "--keep-work",
        action="store_true",
        help="retain the synthesized submissions and evaluator output",
    )
    return parser.parse_args()


def _task_dirs(tasks_root: Path, task_ids: list[str] | None) -> list[Path]:
    if task_ids:
        tasks = [tasks_root / task_id for task_id in task_ids]
    else:
        tasks = sorted(
            path
            for path in tasks_root.iterdir()
            if path.is_dir() and (path / "metadata.json").is_file()
        )
    missing = [path.name for path in tasks if not (path / "metadata.json").is_file()]
    if missing:
        raise ValueError(f"unknown task ids: {', '.join(missing)}")
    return tasks


def _public_spec(task_dir: Path) -> dict[str, Any]:
    metadata = json.loads((task_dir / "metadata.json").read_text(encoding="utf-8"))
    spec = metadata.get("public_spec")
    return spec if isinstance(spec, dict) else {}


def _fingerprint(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _outcome(result: dict[str, Any]) -> dict[str, Any]:
    scores = result.get("scores") or {}
    errors = [str(item) for item in (result.get("errors") or [])]
    return {
        "status": result.get("status"),
        "build_pass": result.get("build_pass"),
        "public_tests_pass": result.get("public_tests_pass"),
        "hidden_tests_pass": result.get("hidden_tests_pass"),
        "isolation_pass": result.get("isolation_pass"),
        "functional_gate": scores.get("functional_gate"),
        "evaluation_capsule_digest": result.get("evaluation_capsule_digest"),
        "errors": errors[:12],
    }


def _first_block(outcome: dict[str, Any]) -> str:
    """Which stage stopped the upstream-direct submission."""
    for key, label in (
        ("build_pass", "build"),
        ("public_tests_pass", "public"),
        ("hidden_tests_pass", "hidden"),
        ("isolation_pass", "isolation"),
    ):
        if outcome.get(key) is False:
            return label
    return "none"


def _block_mechanism(outcome: dict[str, Any]) -> str:
    """Separate "the isolation layer refused it" from "it behaved wrongly".

    A path-based re-export of the pinned upstream normally trips
    ``forbidden_imports`` before any behavior is exercised. That is a real
    property of the benchmark, but it is weaker evidence than a behavioral
    failure, and a task with an empty ``forbidden_imports.txt`` will not be
    stopped that way at all. Recording the mechanism keeps the two apart.
    """
    joined = " ".join(outcome.get("errors") or []).lower()
    if "forbidden module" in joined or "isolation audit blocked" in joined:
        return "isolation_refused_upstream_import"
    if outcome.get("isolation_pass") is False:
        return "isolation_refused_upstream_import"
    if outcome.get("build_pass") is False:
        return "submission_did_not_build"
    if outcome.get("functional_gate") == 1.0:
        return "upstream_satisfied_contract"
    return "behavioral_failure"


def _audit_one(
    task_dir: Path, output_root: Path, image: str, keep_work: bool
) -> dict[str, Any]:
    task_id = task_dir.name
    record: dict[str, Any] = {"task_id": task_id, "gate": GATE_ID}

    up_root = ENTAILMENT.upstream_root(task_dir)
    if up_root is None:
        record.update(
            status=UNDETERMINED,
            reason="task has no pinned repo/ to submit",
            evidence_strength="none",
        )
        return record

    public_spec = _public_spec(task_dir)
    contract = ENTAILMENT.Contract(public_spec)
    if not contract.tops:
        record.update(
            status=UNDETERMINED,
            reason="public_spec declares no featurelifted top-level API",
            evidence_strength="none",
        )
        return record

    work = output_root / "work" / task_id
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True, exist_ok=True)
    submission = work / "submission"
    eval_output = work / "eval"
    submission.mkdir(parents=True, exist_ok=True)
    eval_output.mkdir(parents=True, exist_ok=True)

    try:
        index = ENTAILMENT.index_upstream(up_root)
        stubbed = ENTAILMENT.build_shim(
            submission, up_root, contract, public_spec, index
        )
    except Exception as exc:  # noqa: BLE001
        record.update(
            status=UNDETERMINED,
            reason=f"could not synthesize the upstream submission: "
            f"{type(exc).__name__}: {exc}",
            evidence_strength="none",
        )
        return record

    record["stubbed_names"] = sorted(stubbed)
    try:
        result = evaluate_submission_docker(
            task_dir, submission, eval_output, image=image
        )
    except Exception as exc:  # noqa: BLE001
        record.update(
            status=UNDETERMINED,
            reason=f"evaluator error: {type(exc).__name__}: {exc}",
            evidence_strength="none",
        )
        return record

    outcome = _outcome(result)
    record["outcome"] = outcome
    record["fingerprint"] = _fingerprint(outcome)
    record["first_block"] = _first_block(outcome)
    mechanism = _block_mechanism(outcome)
    record["block_mechanism"] = mechanism

    if outcome.get("functional_gate") == 1.0:
        record.update(
            status=FAIL,
            reason="verbatim upstream re-export satisfies the full contract",
            evidence_strength="strong",
        )
    elif mechanism == "isolation_refused_upstream_import":
        record.update(
            status=PASS,
            reason="the isolation layer refused the upstream import before any "
            "behavior ran, so this says nothing about the contract itself",
            evidence_strength="isolation_only",
        )
    elif stubbed:
        record.update(
            status=PASS,
            reason="upstream does not satisfy the contract, but the task invents "
            "names that were stubbed, so this is not behavioral evidence",
            evidence_strength="reshaped",
        )
    else:
        record.update(
            status=PASS,
            reason=f"upstream re-export fails at {record['first_block']}",
            evidence_strength="strong",
        )

    if not keep_work and record["status"] == PASS:
        shutil.rmtree(work, ignore_errors=True)
    return record


def _image_identity(image: str) -> dict[str, str]:
    completed = subprocess.run(
        ["docker", "image", "inspect", image, "--format", "{{.Id}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    return {"name": image, "id": completed.stdout.strip(), "backend": "docker"}


def _write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    lines = [
        "# G2' — upstream-direct submission audit",
        "",
        "> The unmodified pinned `repo/`, re-exported under the declared",
        "> `required_api` and submitted directly, must **not** pass. A pass means",
        "> the task is solvable by verbatim upstream copy.",
        "",
        f"- Gate: **{'PASS' if payload['gate_pass'] else 'FAIL'}**",
        f"- Evaluator: `{payload['environment']['name']}`",
        f"- Tasks audited: {summary['task_count']}",
        f"- Cleared: {summary['pass']} (behavioral {summary['pass_strong']}, "
        f"reshaped {summary['pass_reshaped']}, "
        f"isolation-only {summary['pass_isolation_only']})",
        f"- Blocking defects: {summary['fail']}",
        f"- Undetermined: {summary['undetermined']}",
        "",
        "`isolation-only` clears carry the least weight: `forbidden_imports`",
        "refused the upstream import before any behavior ran. A task with an",
        "empty `forbidden_imports.txt` cannot be cleared that way, so the split",
        "below is the informative part of this ledger.",
        "",
    ]
    if summary["block_mechanism_counts"]:
        lines += ["## Blocking mechanism", "", "| Mechanism | Tasks |",
                  "| --- | ---: |"]
        for mechanism, count in sorted(summary["block_mechanism_counts"].items()):
            lines.append(f"| `{mechanism}` | {count} |")
        lines.append("")
    if payload["failed_task_ids"]:
        lines += [
            "## Blocking: upstream copy passes",
            "",
            "These tasks are satisfied by verbatim upstream re-export.",
            "",
        ] + [f"- `{task_id}`" for task_id in payload["failed_task_ids"]] + [""]
    if payload["undetermined_task_ids"]:
        lines += ["## Undetermined", ""] + [
            f"- `{task_id}`" for task_id in payload["undetermined_task_ids"]
        ] + [""]
    if summary["first_block_counts"]:
        lines += ["## First blocking stage on cleared tasks", "", "| Stage | Tasks |",
                  "| --- | ---: |"]
        for stage, count in sorted(payload["summary"]["first_block_counts"].items()):
            lines.append(f"| {stage} | {count} |")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = _parse_args()
    if args.workers < 1:
        raise ValueError("--workers must be positive")
    os.environ.setdefault("FEATURELIFTBENCH_SOURCE_REGISTRY", str(SOURCE_REGISTRY))
    os.environ.setdefault("FEATURELIFTBENCH_REFERENCE_REGISTRY", str(REFERENCE_REGISTRY))

    tasks_root = args.tasks_root.resolve()
    tasks = _task_dirs(tasks_root, args.task_ids)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(_audit_one, task, output, args.image, args.keep_work): task.name
            for task in tasks
        }
        for index, future in enumerate(as_completed(futures), start=1):
            record = future.result()
            records.append(record)
            print(
                f"[{index:03d}/{len(tasks):03d}] {record['status'].upper():13} "
                f"{record.get('first_block', '-'):9} {record['task_id']}",
                flush=True,
            )
    records.sort(key=lambda item: str(item["task_id"]))

    failed = [str(r["task_id"]) for r in records if r["status"] == FAIL]
    undetermined = [str(r["task_id"]) for r in records if r["status"] == UNDETERMINED]
    cleared = [r for r in records if r["status"] == PASS]
    first_block_counts: dict[str, int] = {}
    block_mechanism_counts: dict[str, int] = {}
    for record in cleared:
        stage = str(record.get("first_block") or "unknown")
        first_block_counts[stage] = first_block_counts.get(stage, 0) + 1
        mechanism = str(record.get("block_mechanism") or "unknown")
        block_mechanism_counts[mechanism] = block_mechanism_counts.get(mechanism, 0) + 1

    payload = {
        "schema_version": SCHEMA_VERSION,
        "gate": GATE_ID,
        "generated_at": datetime.now(UTC).isoformat(),
        "tasks_root": str(tasks_root.relative_to(ROOT)),
        "environment": _image_identity(args.image),
        "gate_pass": not failed,
        "summary": {
            "task_count": len(records),
            "pass": len(cleared),
            "pass_strong": sum(
                1 for r in cleared if r.get("evidence_strength") == "strong"
            ),
            "pass_reshaped": sum(
                1 for r in cleared if r.get("evidence_strength") == "reshaped"
            ),
            "pass_isolation_only": sum(
                1 for r in cleared if r.get("evidence_strength") == "isolation_only"
            ),
            "fail": len(failed),
            "undetermined": len(undetermined),
            "first_block_counts": first_block_counts,
            "block_mechanism_counts": block_mechanism_counts,
        },
        "failed_task_ids": failed,
        "undetermined_task_ids": undetermined,
        "records": records,
    }
    (output / "summary.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    _write_markdown(payload, output / "summary.md")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0 if payload["gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
